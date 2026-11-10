# How the synthetic profiles were generated

`profile_02` to `profile_10` in `all_profiles.txt` were written by an LLM (a chat assistant, no API
or pipeline code) with few-shot prompting. The only example in the prompt was `profile_01`
(the author's own profile, without contact info), used as a guide for the **format and style**.
All people and companies in the output are fictional.

The prompt (the example profile is pasted at the end, under `## EXAMPLE PROFILE`):

```text
You are generating synthetic LinkedIn-style profiles for a data science
exercise (graph + clustering analysis). All people and organizations you
create are FICTIONAL, but the setting is realistic Iran.

## Fictional organization
"Parsa Data Systems", a mid-size Iranian tech company headquartered in
Tehran with 4 teams: ML Platform, Data Analytics, Backend Engineering,
Product & People.

## Task
Using the EXAMPLE PROFILE below only as a guide for FORMAT and WRITING STYLE
(sections, level of detail, tone), write 9 new, different profiles as plain
text in English. Do NOT copy the example's field, employers, schools or
skills. Keep the same section layout, including "Network".

## Required sections in every profile
Name | Headline | Location | Network | About | Experience (2-4 roles with
title, company, dates, 1-2 line description) | Education (1-2 entries) |
Skills (6-12) | Languages | Interests (3-5) | Recent Activity (2-3 posts
or interactions)

## Iranian context
- Persian names written in Latin script (first + last name), a mix of men
  and women, realistic and common (e.g. Sara Karimi, Mohammad Ahmadi).
  Do not use famous people's names.
- Locations: Tehran mostly, plus a few in Isfahan, Shiraz, Tabriz, Mashhad.
- Education: Iranian universities (e.g. University of Tehran, Sharif
  University of Technology, Amirkabir University of Technology, University
  of Isfahan, Shiraz University, University of Tabriz, Allameh Tabataba'i
  University), plus at most one or two with a foreign master's/PhD.
- Previous employers: FICTIONAL Iranian companies and startups only
  (invent names; do not use real companies).
- Languages: Persian (native) for everyone, English at different levels,
  some with German or Arabic.
- Activity may mention Persian-language posts or local tech/university
  events (describe them in English).
- Dates use Gregorian years.

## Constraints for graph analysis
- All 9 currently work at Parsa Data Systems, spread across the 4 teams.
- Diverse roles: ML engineer, data analyst, backend developer, product
  manager, HR/recruiter, engineering manager, etc. Different fields, not
  cognitive science.
- Realistic overlaps: some pairs share a PREVIOUS employer, some share a
  university, many share a few skills.
- Two people act as "bridges": an engineering manager connected to both ML
  Platform and Backend, and a product manager connected to Analytics and
  Backend.
- Activity items must mention or react to colleagues by exact name
  (e.g. "Commented on <Name>'s post about ..."). Every named person must be
  one of the 10 profiles.
- Connection to the example person (Erfan Eslamieh), who is an EXTERNAL
  collaborator, not a Parsa employee:
  * one Parsa person studied at the Institute for Cognitive Science
    Studies or the University of Isfahan,
  * one Parsa person commented on or reacted to Erfan's post in Activity,
  * two or three share skills such as Python, NumPy, Machine Learning, LLM.
- Output each profile separated by a line: ===== PROFILE n ===== (n = 2..10)

## EXAMPLE PROFILE
<profile_01 text>
```

`extract.py` only links names that are one of the 10 profiles, so a wrong name in an activity line
cannot create a link to a person who does not exist.