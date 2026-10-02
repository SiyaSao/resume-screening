from langgraph.graph import StateGraph, START, END
from agent.state import RecruitmentState
from agent.node import (
    analyze_job_node,
    analyze_resume_node,
    retrieve_context_node,
    match_candidate_node
)
# CREATE WORKFLOW
workflow = StateGraph(
    RecruitmentState
)

# ADD NODES
workflow.add_node(
    "analyze_job",
    analyze_job_node
)

workflow.add_node(
    "analyze_resume",
    analyze_resume_node
)

workflow.add_node(
    "retrieve_context",
    retrieve_context_node
)

workflow.add_node(
    "match_candidate",
    match_candidate_node
)
# CONNECT WORKFLOW
workflow.add_edge(
    START,
    "analyze_job"
)

workflow.add_edge(
    "analyze_job",
    "analyze_resume"
)

workflow.add_edge(
    "analyze_resume",
    "retrieve_context"
)

workflow.add_edge(
    "retrieve_context",
    "match_candidate"
)

workflow.add_edge(
    "match_candidate",
    END
)

# COMPILE GRAPH
recruitment_graph = workflow.compile()