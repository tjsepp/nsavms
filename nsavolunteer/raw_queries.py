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
evt.eventName,
volunteerDate,
volunteerHours
FROM
volunteerHours vh
join familyProfile fp
	on fp.FamilyProfileId = vh.family
join authtools_user au
	on au.id = volunteer
join schoolYear sc
	on vh.SchoolYear = sc.yearId
join nsaEvents evt
	on evt.eventId = vh.event
where vh.approved = 1
and sc.currentYear = 1
and FamilyProfileId =%s
Union all
SELECT
name,
'Traffic' as Type,
Relatedfamily as family,
familyname,
sc.schoolYear as year,
'Traffic Duty',
trafficDutyWeekEnd,
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
and sc.currentYear = 1
Union all
SELECT
name,
'Reward Card' as Type,
Relatedfamily as family,
familyname,
sc.schoolYear as year,
'King Soopers',
refillDate,
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
and sc.currentYear = 1
order by 4,5,1,2
"""

currentVsPriorYear = """
SELECT
yearName,
sum(volunteerHours) as totalHours
FROM
(
	SELECT
    vh.*,
    sy.schoolYear as yearName
    FROM
    volunteerHours vh
    Join schoolYear sy
    	on vh.SchoolYear = sy.yearId
    where
    vh.schoolYear = 3
    and volunteerDate <=DATE_ADD(CURRENT_DATE,INTERVAL -1 YEAR)
    Union
    SELECT
    vh.*,
    sy.schoolYear as yearName
    FROM
    volunteerHours vh
    Join schoolYear sy
    	on vh.SchoolYear = sy.yearId
    where
    vh.schoolYear = 4
    and volunteerDate <=CURRENT_DATE
) agg
group by yearName
"""


DASHBOARD_FAMILY_TOTALS='''
select
fp.familyProfileId,
fp.trafficReq,
fp.volunteerReq,
volHrs.schoolYear,
volHrs.volunteerHours,
pndHrs.pendingHours,
rwcard.rewardCardHours,
tr.trafficDutyHours,
tr.totalShifts,
volHrs.volunteerHours+rwcard.rewardCardHours+tr.trafficDutyHours as totalHours
 from
 familyProfile fp
Left join
(
select
	family,
	schoolYear,
	sum(volunteerHours) as volunteerHours
	from
	volunteerHours
	where approved = 1
	and schoolYear = 5
	group by family,schoolYear) volHrs
on fp.FamilyProfileId = volhrs.family
left join
(
select
	family,
	schoolYear,
	sum(volunteerHours) as pendingHours
	from
	volunteerHours
	where approved = 0
	and schoolYear = 5
	group by family,schoolYear) pndHrs
on pndHrs.family = volHrs.family
and pndHrs.schoolYear = volHrs.SchoolYear
left join
	(
		select
		relatedFamily,
		schoolYear,
		sum(volunteerHours) as rewardCardHours
		from
		rewardCardData
		where
		schoolYear = 5
		group by relatedFamily,schoolYear
		) rwcard
		on  rwcard.relatedFamily = volHrs.family
	and rwcard.schoolYear = volHrs.SchoolYear
left join
	(
		select
		relatedFamily,
		schoolYear,
		sum(volunteerHours) as trafficDutyHours,
		sum(totalTrafficShifts) as totalShifts
		from
		traffic_Duty
		where
		schoolYear = 5
		group by relatedFamily,schoolYear
		) tr
		on  tr.relatedFamily = volHrs.family
	and tr.schoolYear = volHrs.SchoolYear
where
fp.familyProfileId in (select familyprofile_id from familyVolunteers where user_id = 1)
'''

