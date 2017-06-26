bad_familyAgg_records ="""
SELECT
family,
ls.familyName,
sy.schoolYear,
totalHoursSum,
totHoursFromAgg
from(
SELECT
family,
fp.familyName,
ix.schoolYear,
sum(totalHrs) as totalHoursSum,
ag.totalVolunteerHours as totHoursFromAgg
from(
   SELECT
    family,
    schoolYear,
    sum(volunteerHours) as totalHrs
    from(
    SELECT
    family,
    schoolYear,
    volunteerHours
    FROM
    volunteerHours
    where approved = 1) ix
    group by family,schoolYear
    union all
    SELECT
    relatedFamily as family,
    schoolYear,
    sum(volunteerHours) as totalHrs
    from(
        SELECT
        relatedFamily,
        schoolYear,
        volunteerHours
        FROM
        traffic_Duty
    ) ix
    group by relatedFamily,schoolYear
    union all
    SELECT
    relatedFamily as family,
    schoolYear,
    sum(volunteerHours) as totalHrs
    from(
        SELECT
        relatedFamily,
        schoolYear,
        volunteerHours
        FROM
        rewardCardData
    ) ix
    group by relatedFamily,schoolYear
)ix
join familyProfile fp
	on fp.FamilyProfileId = ix.family
join familyAggregate ag
	on ag.relatedFamily = ix.family
    and ag.schoolYear = ix.schoolYear
group by family,fp.familyName,ix.schoolYear
) ls
join schoolYear sy
on sy.yearId = ls.schoolYear
where totalHoursSum<>totHoursFromAgg
"""


FAMILY_DATA_CONSOLIDATED = """
SELECT
name,
'Volunteer' as Type,
Family as family,
familyname,
sc.schoolYear as year,
volunteerHours
FROM
volunteerHours vh
join familyProfile fp
	on fp.FamilyProfileId = vh.family
join authtools_user au
	on au.id = volunteer
join schoolYear sc
	on vh.SchoolYear = sc.yearId
where vh.approved = 1
and FamilyProfileId =%s
Union all
SELECT
name,
'Traffic' as Type,
Relatedfamily as family,
familyname,
sc.schoolYear as year,
volunteerHours
FROM
traffic_Duty vh
join familyProfile fp
	on fp.FamilyProfileId = vh.relatedfamily
join authtools_user au
	on au.id = volunteer
join schoolYear sc
	on vh.SchoolYear = sc.yearId
where FamilyProfileId =%s
Union all
SELECT
name,
'Reward Card' as Type,
Relatedfamily as family,
familyname,
sc.schoolYear as year,
volunteerHours
FROM
rewardCardData vh
join familyProfile fp
	on fp.FamilyProfileId = vh.relatedfamily
join authtools_user au
	on au.id = volunteer
join schoolYear sc
	on vh.SchoolYear = sc.yearId
where FamilyProfileId =%s
order by 4,5,1,2
"""