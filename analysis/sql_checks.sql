-- Roadmap priority review
select workflow_id, workflow, priority_score, launch_status, next_decision
from roadmap_queue
order by priority_score desc
limit 10;

-- PRD requirements needing review
select requirement_id, workflow_id, severity, evidence_source, prd_status
from prd_cards
where severity in ('High', 'Critical')
order by request_count desc;

-- Launch gates below threshold
select workflow_id, workflow, readiness_score, weakest_gate, owner_team
from readiness_register
where readiness_score < 72
order by readiness_score asc;
