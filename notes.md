# نسخه فارسی

در این پروژه چیزی از اینترنت استخراج نشده و داده‌ها از یک فایل متنی خوانده می‌شوند. پروفایل ۱ واقعی است و ۲ تا ۱۰ ساختگی‌اند، پس نتایج فقط کارکرد pipeline را نشان می‌دهند.

## فرضیات و طراحی

- یال‌های گراف از دو چیز ساخته می‌شوند، تعامل‌های داخل activity (وزن ۲) و کارفرمای قبلی یا دانشگاه مشترک (وزن ۱). کارفرمای فعلی نادیده گرفته می‌شود چون برای همه یکی است.
- گراف بدون جهت است. betweenness بدون وزن حساب می‌شود، چون NetworkX وزن را فاصله در نظر می‌گیرد و در اینجا وزن بیشتر یعنی ارتباط نزدیک‌تر. PageRank از وزن‌ها استفاده می‌کند.
- مهارت‌ها با TF-IDF و KMeans خوشه‌بندی شدند و تعداد خوشه‌ها با silhouette انتخاب شد. امتیازها پایین است و خوشه‌ها ضعیف‌اند.
- نام‌ها با تطبیق ساده‌ی رشته پیدا می‌شوند، پس نام کوتاه‌شده یا مستعار از دست می‌رود.

## اگر استخراج آنلاین بود

لینکدین طبق شرایط استفاده، استخراج خودکار را ممنوع کرده است. در عمل باید از API رسمی یا داده‌ی دارای مجوز استفاده کرد. از نظر فنی:

- **HTTP:** یک session برای هر worker با timeout مناسب، retry فقط برای خطاهای موقت (429 و 5xx) با backoff، و ذخیره‌ی پاسخ خام پیش از پردازش.
- **Headers:** User-Agent شفاف که ابزار و راه تماس را معرفی کند. تقلید مرورگر یا تعویض هویت برای دور زدن محدودیت درست نیست.
- **Rate limiting:** محدودیت نرخ برای هر host با token bucket، رعایت `Retry-After`، و cache برای جلوگیری از درخواست تکراری.

## پردازش با صف

Producer آدرس پروفایل‌ها را در صف می‌گذارد، workerهای fetch صفحه را می‌گیرند و ذخیره می‌کنند، workerهای parse آن را به JSON تبدیل می‌کنند و در پایان تحلیل گراف روی داده‌های آماده اجرا می‌شود. رکوردهای ناموفق به dead-letter queue می‌روند. اگر replay و حجم بالا مهم باشد Kafka مناسب است و برای شروع و حجم کم Redis ساده‌تر است. پردازش باید idempotent باشد (با upsert روی شناسه‌ی پروفایل) تا پیام تکراری مشکلی ایجاد نکند.

## ذخیره‌سازی در مقیاس بزرگ

- پاسخ‌های خام در object storage (مثل S3)
- داده‌ی پردازش‌شده با قالب Parquet
- برای جست‌وجو و پرس‌وجو، PostgreSQL با جدول‌های جدا برای پروفایل، شغل، تحصیل و مهارت، و یک جدول برای یال‌ها
- ثبت زمان دریافت و نسخه‌ی schema در هر رکورد، و امکان حذف داده‌ی یک فرد از همه‌ی لایه‌ها

## محدودیت‌ها

- parser فقط یک قالب متنی را می‌خواند.
- فقط ۱۰ پروفایل داریم و ۹ تا ساختگی است.
- یال‌ها جهت ندارند.
- رتبه‌های هم‌مقدار مساوی‌اند و یک یال می‌تواند سه نفر اول را عوض کند.


---


# English version

Nothing was scraped online in this project. The data is read from a text file. Profile 1 is real and profiles 2 to 10 are synthetic, so the results only show that the pipeline works.

## Assumptions and design

- Graph links come from two things, interactions in the activity text (weight 2) and a shared past employer or university (weight 1). The current employer is ignored because it is the same for everyone.
- The graph is undirected. Betweenness is computed without weights, because NetworkX treats a weight as a distance, while here a larger weight means a closer tie. PageRank uses the weights.
- Skills are clustered with TF-IDF and KMeans, and the number of clusters is picked with the silhouette score. The scores are low, so the clusters are weak.
- Names are matched as plain strings, so a shortened name or nickname would be missed.

## If extraction were done online

LinkedIn's terms forbid automated scraping. In practice an official API or licensed data should be used. On the technical side:

- **HTTP:** one session per worker with sensible timeouts, retries only on temporary errors (429, 5xx) with backoff, and saving the raw response before parsing.
- **Headers:** a transparent User-Agent that names the tool and gives a contact. Faking a browser or rotating identities to avoid limits is not acceptable.
- **Rate limiting:** a per-host limit with a token bucket, respect for `Retry-After`, and a cache to avoid repeated requests.

## Queue processing

A producer puts profile URLs in a queue, fetch workers download and store the pages, parse workers turn them into JSON, and the graph analysis runs on the prepared data. Failed records go to a dead-letter queue. Kafka fits when replay and high volume matter, and Redis is simpler for a small start. Processing should be idempotent (upsert on the profile ID), so a repeated message does no harm.

## Storage at scale

- Raw responses in object storage (such as S3)
- Parsed data as Parquet files
- PostgreSQL for querying, with separate tables for profiles, jobs, education and skills, and one table for edges
- A fetch timestamp and schema version in every record, and the ability to delete one person's data from every layer

## Limitations

- The parser reads only one text format.
- There are only 10 profiles, and 9 are synthetic.
- Links have no direction.
- Equal ranks are ties, and one link can change the top three.