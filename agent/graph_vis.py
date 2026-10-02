import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.graph import recruitment_graph

png_data = recruitment_graph.get_graph().draw_mermaid_png()

with open("recruitment_workflow.png", "wb") as f:
    f.write(png_data)

print("Workflow graph created successfully!")