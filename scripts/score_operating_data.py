import csv
import json
import random
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUTS = ROOT / "analysis" / "outputs"
random.seed(5262026)


WORKFLOWS = [
    {
        "workflow_id": "BA001",
        "product_area": "Lawyer matching",
        "workflow": "Best-fit law firm recommendation",
        "persona": "Client advocate",
        "problem": "Clients with viable cases need a fast match that considers jurisdiction, case type, firm capacity, and client preference.",
        "hypothesis": "A transparent matching rubric will raise accepted matches while reducing rework for advocates and firms.",
        "owner_team": "Product and Data Science",
        "roadmap_horizon": "Now",
        "strategic_fit": 96,
        "effort": 64,
        "risk_sensitivity": 92,
    },
    {
        "workflow_id": "BA002",
        "product_area": "Intake",
        "workflow": "Eligibility quiz repair loop",
        "persona": "Benefits applicant",
        "problem": "Ambiguous quiz answers create downstream case review delays and lower confidence in eligibility recommendations.",
        "hypothesis": "A guided repair loop can improve qualification precision without making intake feel bureaucratic.",
        "owner_team": "Product and Design",
        "roadmap_horizon": "Now",
        "strategic_fit": 93,
        "effort": 48,
        "risk_sensitivity": 88,
    },
    {
        "workflow_id": "BA003",
        "product_area": "Client operations",
        "workflow": "Advocate triage command queue",
        "persona": "Client advocate lead",
        "problem": "High-need clients can be buried behind lower-risk follow-ups when urgency and readiness are not visible together.",
        "hypothesis": "A triage queue that combines urgency, readiness, and outreach history will improve first-contact speed.",
        "owner_team": "Client Experience",
        "roadmap_horizon": "Next",
        "strategic_fit": 89,
        "effort": 54,
        "risk_sensitivity": 86,
    },
    {
        "workflow_id": "BA004",
        "product_area": "Marketplace health",
        "workflow": "No-match recovery path",
        "persona": "Marketplace operator",
        "problem": "Some qualified clients cannot be matched immediately because the right firm capacity or jurisdiction fit is unavailable.",
        "hypothesis": "A recovery path with alternate routing and capacity alerts will prevent viable clients from dropping out.",
        "owner_team": "Product Operations",
        "roadmap_horizon": "Now",
        "strategic_fit": 91,
        "effort": 59,
        "risk_sensitivity": 90,
    },
    {
        "workflow_id": "BA005",
        "product_area": "Lawyer network",
        "workflow": "Firm capacity and preference signal",
        "persona": "Partner law firm",
        "problem": "Firm availability, state coverage, case appetite, and response speed can drift faster than manual routing rules.",
        "hypothesis": "Lightweight firm-side capacity signals will improve match acceptance and reduce dead-end referrals.",
        "owner_team": "Lawyer Network",
        "roadmap_horizon": "Next",
        "strategic_fit": 88,
        "effort": 67,
        "risk_sensitivity": 83,
    },
    {
        "workflow_id": "BA006",
        "product_area": "Evidence readiness",
        "workflow": "Document readiness coach",
        "persona": "Benefits applicant",
        "problem": "Clients often do not know which documents or medical evidence are needed before a lawyer evaluates the case.",
        "hypothesis": "A plain-language checklist will raise case readiness and reduce repeated advocate follow-up.",
        "owner_team": "Product and Legal Ops",
        "roadmap_horizon": "Next",
        "strategic_fit": 86,
        "effort": 46,
        "risk_sensitivity": 87,
    },
    {
        "workflow_id": "BA007",
        "product_area": "Case collaboration",
        "workflow": "Post-match client handoff",
        "persona": "Newly matched client",
        "problem": "Clients can lose trust after referral if expectations, next steps, and firm response times are unclear.",
        "hypothesis": "A structured handoff timeline will improve client confidence and firm follow-through.",
        "owner_team": "Product and Design",
        "roadmap_horizon": "Next",
        "strategic_fit": 84,
        "effort": 42,
        "risk_sensitivity": 80,
    },
    {
        "workflow_id": "BA008",
        "product_area": "Case collaboration",
        "workflow": "Milestone status tracker",
        "persona": "Matched client",
        "problem": "Clients need reassurance during long benefits timelines, especially when agencies or insurers move slowly.",
        "hypothesis": "Milestone visibility will reduce avoidable support contacts and improve trust through long waits.",
        "owner_team": "Product and Engineering",
        "roadmap_horizon": "Later",
        "strategic_fit": 78,
        "effort": 71,
        "risk_sensitivity": 72,
    },
    {
        "workflow_id": "BA009",
        "product_area": "New verticals",
        "workflow": "VA benefits evidence checklist",
        "persona": "Veteran applicant",
        "problem": "Veterans need claim-specific evidence guidance that differs from disability and workers compensation journeys.",
        "hypothesis": "A vertical-specific readiness checklist can validate expansion demand before deeper workflow investment.",
        "owner_team": "New Verticals",
        "roadmap_horizon": "Later",
        "strategic_fit": 81,
        "effort": 58,
        "risk_sensitivity": 81,
    },
    {
        "workflow_id": "BA010",
        "product_area": "Workers compensation",
        "workflow": "State-specific routing guardrails",
        "persona": "Injured worker",
        "problem": "State rules, deadlines, and firm coverage create routing complexity for injured workers seeking help.",
        "hypothesis": "State-specific guardrails can reduce mismatches while preserving a simple intake journey.",
        "owner_team": "Product and Legal Ops",
        "roadmap_horizon": "Later",
        "strategic_fit": 82,
        "effort": 62,
        "risk_sensitivity": 84,
    },
]

EVIDENCE_SOURCES = [
    "Client advocate interview",
    "Partner firm interview",
    "Support transcript review",
    "Intake funnel telemetry",
    "Legal ops policy review",
]

REQUIREMENT_TEMPLATES = [
    ("Match rationale", "Show why the recommended firm is a fit before the advocate confirms the referral."),
    ("Capacity freshness", "Flag stale firm availability signals before a match is presented."),
    ("Client expectation", "Explain the next step in plain language at the moment of handoff."),
    ("Exception path", "Route low-confidence cases to review instead of presenting a brittle answer."),
    ("Outcome tracking", "Instrument whether the decision improved speed, trust, or acceptance."),
]

READINESS_GATES = [
    "Problem framing",
    "PRD completeness",
    "Data instrumentation",
    "Legal review",
    "Design prototype",
    "Engineering estimate",
    "Operations playbook",
    "Experiment plan",
]

PUBLIC_BENCHMARKS = [
    {
        "benchmark_id": "PUB-SSA-INITIAL",
        "domain": "Disability determination",
        "metric": "Initial disability claim processing time",
        "benchmark_value": "Monthly elapsed-day benchmark",
        "source": "SSA Open Data",
        "use_in_artifact": "Sets external context for why intake completeness and evidence readiness matter.",
    },
    {
        "benchmark_id": "PUB-SSA-HEARING",
        "domain": "Appeals and hearings",
        "metric": "Hearing processing target",
        "benchmark_value": "270 days",
        "source": "SSA performance reporting",
        "use_in_artifact": "Frames long-cycle trust and status transparency as product risks.",
    },
    {
        "benchmark_id": "PUB-GAO-APPEALS",
        "domain": "Appeals hardship",
        "metric": "Most appealed applicants waited more than one year for final decision in the study period",
        "benchmark_value": "More than one year",
        "source": "GAO disability appeals report",
        "use_in_artifact": "Raises urgency weight for workflows that reduce avoidable delay.",
    },
]

MODEL_ACTIONS = [
    "Personalize next best intake question",
    "Recommend lawyer match with rationale",
    "Route to advocate review before referral",
    "Prompt evidence checklist completion",
    "Escalate delayed handoff follow-up",
]


def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def clamp(value, low, high):
    return max(low, min(high, value))


def build_requirements():
    rows = []
    for workflow in WORKFLOWS:
        selected = random.sample(REQUIREMENT_TEMPLATES, 3)
        for index, (theme, description) in enumerate(selected, start=1):
            severity = random.choice(["High", "High", "Medium", "Medium", "Critical"])
            request_count = random.randint(9, 42)
            confidence = round(random.uniform(0.64, 0.93), 2)
            rows.append(
                {
                    "requirement_id": f"REQ-{workflow['workflow_id']}-{index}",
                    "workflow_id": workflow["workflow_id"],
                    "theme": theme,
                    "persona": workflow["persona"],
                    "evidence_source": random.choice(EVIDENCE_SOURCES),
                    "severity": severity,
                    "request_count": request_count,
                    "confidence": confidence,
                    "user_need": description,
                    "acceptance_criteria": f"{theme} is visible, auditable, and measured before launch review.",
                    "instrumentation": random.choice(
                        [
                            "match_acceptance_rate",
                            "time_to_first_contact_hours",
                            "case_readiness_score",
                            "client_trust_score",
                            "manual_rework_rate",
                        ]
                    ),
                    "prd_status": random.choice(["Drafted", "Needs legal review", "Ready for sizing", "Needs research"]),
                }
            )
    return rows


def build_weekly_metrics():
    rows = []
    weeks = [f"2026-W{week:02d}" for week in range(1, 13)]
    for workflow in WORKFLOWS:
        starts_base = random.randint(480, 1400)
        for week_number, week in enumerate(weeks, start=1):
            maturity = week_number / len(weeks)
            qualified_rate = clamp(random.gauss(0.58 + workflow["strategic_fit"] / 700, 0.04), 0.43, 0.84)
            match_acceptance = clamp(random.gauss(0.49 + workflow["strategic_fit"] / 850 - workflow["effort"] / 900, 0.045), 0.35, 0.78)
            response_hours = clamp(random.gauss(44 - workflow["strategic_fit"] / 6 + workflow["effort"] / 5, 4.8), 8, 72)
            trust_score = clamp(random.gauss(64 + workflow["strategic_fit"] / 4 - workflow["risk_sensitivity"] / 20 + maturity * 4, 3.8), 48, 91)
            readiness = clamp(random.gauss(58 + workflow["strategic_fit"] / 5 - workflow["effort"] / 6 + maturity * 6, 4.2), 35, 92)
            rows.append(
                {
                    "week": week,
                    "workflow_id": workflow["workflow_id"],
                    "intake_starts": int(starts_base * random.uniform(0.88, 1.14)),
                    "qualified_rate": round(qualified_rate, 3),
                    "match_acceptance_rate": round(match_acceptance, 3),
                    "firm_response_hours": round(response_hours, 1),
                    "client_trust_score": round(trust_score, 1),
                    "case_readiness_score": round(readiness, 1),
                    "data_quality_score": round(clamp(random.gauss(82 - workflow["effort"] / 14, 4.0), 62, 96), 1),
                }
            )
    return rows


def build_events():
    rows = []
    event_types = ["User friction", "Firm feedback", "Policy risk", "Data gap", "Support escalation", "Experiment idea"]
    for workflow in WORKFLOWS:
        for index in range(1, 7):
            impact = random.randint(18000, 145000)
            rows.append(
                {
                    "event_id": f"EV-{workflow['workflow_id']}-{index}",
                    "workflow_id": workflow["workflow_id"],
                    "event_type": random.choice(event_types),
                    "source": random.choice(EVIDENCE_SOURCES),
                    "severity": random.choice(["Medium", "High", "High", "Critical"]),
                    "estimated_clients_affected": random.randint(120, 2200),
                    "estimated_impact": impact,
                    "note": random.choice(
                        [
                            "Repeated uncertainty during intake handoff.",
                            "Firm preference mismatch created extra advocate work.",
                            "Client needed clearer plain-language guidance.",
                            "Routing rule did not reflect current capacity.",
                            "Metric was tracked, but not actionable for roadmap review.",
                        ]
                    ),
                }
            )
    return rows


def build_experiments():
    rows = []
    for workflow in WORKFLOWS:
        primary_metric = random.choice(
            [
                "match_acceptance_rate",
                "time_to_first_contact_hours",
                "case_readiness_score",
                "client_trust_score",
                "manual_rework_rate",
            ]
        )
        rows.append(
            {
                "experiment_id": f"EXP-{workflow['workflow_id']}",
                "workflow_id": workflow["workflow_id"],
                "hypothesis": workflow["hypothesis"],
                "primary_metric": primary_metric,
                "guardrail_metric": random.choice(["complaint_rate", "legal_review_hold_rate", "support_reopen_rate"]),
                "sample_plan": random.choice(["Matched cohort", "Geo split", "Advocate-team rollout", "Firm cohort"]),
                "minimum_detectable_lift": f"{random.randint(5, 14)}%",
                "decision_rule": random.choice(
                    [
                        "Ship if primary metric improves and guardrail is flat.",
                        "Iterate if lift appears only in one case type.",
                        "Hold if legal review exceptions increase.",
                    ]
                ),
            }
        )
    return rows


def build_platform_register(roadmap):
    rows = []
    contracts = {
        "intake_quiz": ("Intake event contract", "client_id, state, claim_type, answer_confidence, submitted_at"),
        "advocate_case_notes": ("Advocate disposition contract", "workflow_id, urgency, next_step, review_reason"),
        "lawyer_capacity": ("Firm capacity contract", "state, practice_area, open_slots, response_sla_hours"),
        "client_messages": ("Client message contract", "channel, handoff_step, response_due_at, sentiment_signal"),
        "claim_documents": ("Document evidence contract", "document_type, freshness_days, completeness_score"),
        "case_outcomes": ("Outcome feedback contract", "match_accepted, benefit_stage, payout_status, closed_reason"),
        "public_benchmarks": ("Public benchmark contract", "domain, metric, benchmark_value, source, updated_at"),
    }
    source_by_area = {
        "Lawyer matching": "lawyer_capacity",
        "Intake": "intake_quiz",
        "Client operations": "advocate_case_notes",
        "Marketplace health": "case_outcomes",
        "Lawyer network": "lawyer_capacity",
        "Evidence readiness": "claim_documents",
        "Case collaboration": "client_messages",
        "New verticals": "public_benchmarks",
        "Workers compensation": "public_benchmarks",
    }
    benchmark_cycle = [row["benchmark_id"] for row in PUBLIC_BENCHMARKS]
    for index, workflow in enumerate(roadmap):
        source_domain = source_by_area[workflow["product_area"]]
        contract_name, required_fields = contracts[source_domain]
        quality = float(workflow["avg_data_quality"])
        freshness_hours = random.choice([2, 4, 8, 12, 24, 48])
        missingness = round(clamp((100 - quality) / 130 + random.uniform(0.01, 0.07), 0.02, 0.28), 3)
        decision_confidence = round(clamp(0.54 + workflow["priority_score"] / 260 - missingness, 0.45, 0.92), 2)
        launch_blocker = "None"
        if quality < 74:
            launch_blocker = "Data quality remediation"
        elif freshness_hours > 24:
            launch_blocker = "Freshness SLA"
        elif decision_confidence < 0.68:
            launch_blocker = "Model confidence"

        rows.append(
            {
                "workflow_id": workflow["workflow_id"],
                "workflow": workflow["workflow"],
                "source_domain": source_domain,
                "contract_name": contract_name,
                "required_fields": required_fields,
                "freshness_sla_hours": freshness_hours,
                "missingness_rate": missingness,
                "decision_confidence": decision_confidence,
                "model_action": MODEL_ACTIONS[index % len(MODEL_ACTIONS)],
                "public_benchmark": benchmark_cycle[index % len(benchmark_cycle)],
                "launch_blocker": launch_blocker,
                "owner_team": workflow["owner_team"],
            }
        )
    rows.sort(key=lambda row: (row["launch_blocker"] == "None", row["decision_confidence"]))
    return rows


def score_outputs(requirements, weekly_metrics, events, experiments):
    req_by_workflow = defaultdict(list)
    for row in requirements:
        req_by_workflow[row["workflow_id"]].append(row)

    metrics_by_workflow = defaultdict(list)
    for row in weekly_metrics:
        metrics_by_workflow[row["workflow_id"]].append(row)

    event_by_workflow = defaultdict(list)
    for row in events:
        event_by_workflow[row["workflow_id"]].append(row)

    roadmap = []
    readiness_rows = []
    prd_cards = []
    experiment_rows = []

    for workflow in WORKFLOWS:
        workflow_id = workflow["workflow_id"]
        metrics = metrics_by_workflow[workflow_id]
        latest = metrics[-1]
        reqs = req_by_workflow[workflow_id]
        workflow_events = event_by_workflow[workflow_id]

        avg_acceptance = sum(float(row["match_acceptance_rate"]) for row in metrics) / len(metrics)
        avg_response = sum(float(row["firm_response_hours"]) for row in metrics) / len(metrics)
        avg_quality = sum(float(row["data_quality_score"]) for row in metrics) / len(metrics)
        avg_readiness = sum(float(row["case_readiness_score"]) for row in metrics) / len(metrics)
        total_requests = sum(int(row["request_count"]) for row in reqs)
        critical_count = sum(1 for row in reqs if row["severity"] == "Critical")
        event_impact = sum(int(row["estimated_impact"]) for row in workflow_events)
        friction_score = (1 - avg_acceptance) * 34 + avg_response / 3 + (100 - avg_quality) * 0.55
        priority_score = (
            workflow["strategic_fit"] * 0.34
            + workflow["risk_sensitivity"] * 0.18
            + total_requests * 0.22
            + event_impact / 26000
            + friction_score * 0.9
            - workflow["effort"] * 0.23
            + critical_count * 3.5
        )

        readiness_score = round(clamp(avg_readiness * 0.48 + avg_quality * 0.25 + workflow["strategic_fit"] * 0.27 - workflow["effort"] * 0.12, 0, 100), 1)
        if readiness_score >= 76 and priority_score >= 92:
            launch_status = "Ready to size"
        elif readiness_score >= 67:
            launch_status = "Needs one gate"
        else:
            launch_status = "Discovery first"

        next_decision = {
            "Ready to size": "Size the PRD slice with engineering and legal operations.",
            "Needs one gate": "Close the weakest gate before committing roadmap capacity.",
            "Discovery first": "Run focused discovery before roadmap commitment.",
        }[launch_status]

        weakest_gate = random.choice(READINESS_GATES)
        second_gate = random.choice([gate for gate in READINESS_GATES if gate != weakest_gate])

        roadmap.append(
            {
                **workflow,
                "priority_score": round(priority_score, 1),
                "launch_status": launch_status,
                "next_decision": next_decision,
                "request_count": total_requests,
                "critical_requirements": critical_count,
                "estimated_impact": event_impact,
                "avg_match_acceptance": round(avg_acceptance, 3),
                "avg_firm_response_hours": round(avg_response, 1),
                "avg_data_quality": round(avg_quality, 1),
                "latest_client_trust_score": latest["client_trust_score"],
                "latest_case_readiness_score": latest["case_readiness_score"],
                "readiness_score": readiness_score,
                "weakest_gate": weakest_gate,
                "second_gate": second_gate,
            }
        )

        top_req = sorted(
            reqs,
            key=lambda row: (row["severity"] == "Critical", int(row["request_count"]), float(row["confidence"])),
            reverse=True,
        )[0]
        prd_cards.append(
            {
                **top_req,
                "workflow": workflow["workflow"],
                "product_area": workflow["product_area"],
                "problem": workflow["problem"],
                "hypothesis": workflow["hypothesis"],
                "user_story": f"As a {workflow['persona'].lower()}, I need {top_req['user_need'].lower()}",
                "acceptance_criteria": top_req["acceptance_criteria"],
                "validation_plan": f"Review {top_req['instrumentation']} by case type, state, firm cohort, and advocate team before scaling.",
            }
        )

        readiness_rows.append(
            {
                "workflow_id": workflow_id,
                "workflow": workflow["workflow"],
                "product_area": workflow["product_area"],
                "launch_status": launch_status,
                "readiness_score": readiness_score,
                "weakest_gate": weakest_gate,
                "second_gate": second_gate,
                "owner_team": workflow["owner_team"],
                "next_decision": next_decision,
            }
        )

        experiment = next(row for row in experiments if row["workflow_id"] == workflow_id)
        experiment_rows.append(
            {
                **experiment,
                "workflow": workflow["workflow"],
                "product_area": workflow["product_area"],
                "launch_status": launch_status,
                "priority_score": round(priority_score, 1),
                "readiness_score": readiness_score,
            }
        )

    roadmap.sort(key=lambda row: row["priority_score"], reverse=True)
    prd_cards.sort(key=lambda row: (row["severity"] == "Critical", int(row["request_count"]), float(row["confidence"])), reverse=True)
    readiness_rows.sort(key=lambda row: row["readiness_score"])
    experiment_rows.sort(key=lambda row: row["priority_score"], reverse=True)
    return roadmap, prd_cards, readiness_rows, experiment_rows


def write_markdown(summary, roadmap, prd_cards, readiness_rows, platform_rows):
    top = roadmap[0]
    top_platform = platform_rows[0]
    (ROOT / "analysis" / "executive_findings.md").write_text(
        "\n".join(
            [
                "# Executive Findings",
                "",
                "## What I analyzed",
                "",
                f"I generated and scored {summary['workflow_count']} benefits access product workflows, {summary['requirement_count']} PRD requirements, {summary['event_count']} stakeholder evidence events, and {summary['weekly_metric_count']} weekly operating rows.",
                "",
                "## Findings",
                "",
                f"- The highest-priority roadmap bet is {top['workflow']} with a priority score of {top['priority_score']}.",
                f"- The top workflow combines {top['request_count']} evidence-backed requests, {top['avg_match_acceptance']:.0%} average match acceptance, and ${top['estimated_impact']:,} modeled opportunity.",
                f"- The weakest launch gate for the top workflow is {top['weakest_gate']}, which makes cross-functional alignment the next product-management task.",
                f"- The highest-risk data-platform contract is {top_platform['contract_name']} for {top_platform['workflow']}, with {top_platform['decision_confidence']:.0%} model-decision confidence.",
                "",
                "## Recommendation",
                "",
                "Use the roadmap queue to select one PRD slice, close the weakest launch gate, verify the data contract, and run the linked experiment before broad rollout.",
                "",
            ]
        )
    )

    (ROOT / "analysis" / "analysis_plan.md").write_text(
        "\n".join(
            [
                "# Analysis Plan",
                "",
                "1. Model the client intake, lawyer matching, evidence readiness, and case collaboration workflows at product-decision grain.",
                "2. Generate synthetic stakeholder evidence, PRD requirements, weekly operating metrics, and experiment plans.",
                "3. Score each workflow using strategic fit, request volume, evidence severity, marketplace friction, data quality, modeled opportunity, and effort.",
                "4. Convert the highest-priority workflow into a PRD slice with acceptance criteria, instrumentation, and validation plan.",
                "5. Review data contracts, freshness, missingness, public benchmark context, and model-decision confidence before committing roadmap capacity.",
                "6. Review launch readiness gates before scaling the experiment.",
                "",
            ]
        )
    )

    (ROOT / "analysis" / "methodology.md").write_text(
        "\n".join(
            [
                "# Methodology",
                "",
                "The analysis uses deterministic synthetic data because real client intake, legal case, law-firm capacity, support, and outcome data would be private.",
                "",
                "The scoring model combines strategic fit, client-risk sensitivity, PRD request volume, critical requirement count, stakeholder event impact, match acceptance, firm response time, data quality, and implementation effort.",
                "",
                "Synthetic distributions use bounded random draws around realistic product operating ranges: match acceptance from 35% to 78%, firm response from 8 to 72 hours, data quality from 62 to 96, and client trust from 48 to 91.",
                "",
                "The data-platform register adds source-domain freshness, required-field completeness, missingness, and model-decision confidence. Public benchmarks from SSA and GAO are used only as contextual anchors for wait-time and appeals risk, not as company performance claims.",
                "",
                "The data does not represent any real person, law firm, claim, client, employer, agency, insurer, or company performance.",
                "",
            ]
        )
    )

    (ROOT / "analysis" / "sql_checks.sql").write_text(
        "\n".join(
            [
                "-- Roadmap priority review",
                "select workflow_id, workflow, priority_score, launch_status, next_decision",
                "from roadmap_queue",
                "order by priority_score desc",
                "limit 10;",
                "",
                "-- PRD requirements needing review",
                "select requirement_id, workflow_id, severity, evidence_source, prd_status",
                "from prd_cards",
                "where severity in ('High', 'Critical')",
                "order by request_count desc;",
                "",
                "-- Launch gates below threshold",
                "select workflow_id, workflow, readiness_score, weakest_gate, owner_team",
                "from readiness_register",
                "where readiness_score < 72",
                "order by readiness_score asc;",
                "",
                "-- Data-platform contracts needing launch attention",
                "select workflow_id, workflow, contract_name, source_domain, decision_confidence, launch_blocker",
                "from platform_readiness",
                "where launch_blocker <> 'None'",
                "order by decision_confidence asc;",
                "",
            ]
        )
    )


def main():
    DATA.mkdir(exist_ok=True)
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    requirements = build_requirements()
    weekly_metrics = build_weekly_metrics()
    events = build_events()
    experiments = build_experiments()
    roadmap, prd_cards, readiness_rows, experiment_rows = score_outputs(requirements, weekly_metrics, events, experiments)
    platform_rows = build_platform_register(roadmap)

    write_csv(DATA / "product_workflows.csv", WORKFLOWS, list(WORKFLOWS[0].keys()))
    write_csv(DATA / "prd_requirements.csv", requirements, list(requirements[0].keys()))
    write_csv(DATA / "weekly_operating_metrics.csv", weekly_metrics, list(weekly_metrics[0].keys()))
    write_csv(DATA / "stakeholder_events.csv", events, list(events[0].keys()))
    write_csv(DATA / "experiment_plans.csv", experiments, list(experiments[0].keys()))
    write_csv(DATA / "public_benchmarks.csv", PUBLIC_BENCHMARKS, list(PUBLIC_BENCHMARKS[0].keys()))

    roadmap_fields = list(roadmap[0].keys())
    prd_fields = list(prd_cards[0].keys())
    readiness_fields = list(readiness_rows[0].keys())
    experiment_fields = list(experiment_rows[0].keys())
    platform_fields = list(platform_rows[0].keys())
    write_csv(OUTPUTS / "roadmap_queue.csv", roadmap, roadmap_fields)
    write_csv(OUTPUTS / "prd_cards.csv", prd_cards, prd_fields)
    write_csv(OUTPUTS / "readiness_register.csv", readiness_rows, readiness_fields)
    write_csv(OUTPUTS / "experiment_readout.csv", experiment_rows, experiment_fields)
    write_csv(OUTPUTS / "platform_readiness.csv", platform_rows, platform_fields)

    summary = {
        "workflow_count": len(WORKFLOWS),
        "requirement_count": len(requirements),
        "event_count": len(events),
        "weekly_metric_count": len(weekly_metrics),
        "experiment_count": len(experiments),
        "top_workflow": roadmap[0],
        "ready_to_size": sum(1 for row in roadmap if row["launch_status"] == "Ready to size"),
        "data_contract_count": len({row["contract_name"] for row in platform_rows}),
        "platform_blockers": sum(1 for row in platform_rows if row["launch_blocker"] != "None"),
        "needs_one_gate": sum(1 for row in roadmap if row["launch_status"] == "Needs one gate"),
        "discovery_first": sum(1 for row in roadmap if row["launch_status"] == "Discovery first"),
        "modeled_impact": sum(row["estimated_impact"] for row in roadmap),
    }

    payload = {
        "summary": summary,
        "workflows": WORKFLOWS,
        "roadmapQueue": roadmap,
        "prdCards": prd_cards,
        "readinessRegister": readiness_rows,
        "experimentReadout": experiment_rows,
        "platformReadiness": platform_rows,
        "publicBenchmarks": PUBLIC_BENCHMARKS,
        "stakeholderEvents": events,
    }
    (OUTPUTS / "summary.json").write_text(json.dumps(summary, indent=2))
    (OUTPUTS / "app_payload.json").write_text(json.dumps(payload, indent=2))
    write_markdown(summary, roadmap, prd_cards, readiness_rows, platform_rows)

    print(f"Top workflow: {roadmap[0]['workflow']} ({roadmap[0]['priority_score']})")
    print(f"Launch status: {roadmap[0]['launch_status']}")
    print(f"Modeled opportunity: ${summary['modeled_impact']:,}")


if __name__ == "__main__":
    main()
