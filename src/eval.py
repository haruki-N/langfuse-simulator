import trace
from dotenv import load_dotenv
from langfuse.api import DatasetRunItem, TraceWithFullDetails
load_dotenv()

from langfuse import Evaluation, get_client
from pprint import pprint
from typing import Any



CONSICENESS_PROMPT="""
"""

GOAL_ACCOMPLISHNESS_PROMPT="""
"""

class RunEvaluator():
  def __init__(self, dataset_name: str="simulated-conversations"):
    self.dataset_name = dataset_name
    self.langfuse = get_client()

  def fetch_latest_run(self):
    runs = self.langfuse.get_dataset_runs(dataset_name=self.dataset_name, page=1, limit=1)
    if runs.data:
      latest_run = self.langfuse.get_dataset_run(dataset_name=self.dataset_name, run_name=runs.data[0].name)
      return latest_run
    return None

  def get_observations_for_eval(self):
    observations = []
    latest_run = self.fetch_latest_run()
    dataset_run_items = latest_run.dataset_run_items

    for run_item in dataset_run_items:
      trace_id = run_item.trace_id
      related_trace = self.langfuse.api.trace.get(trace_id=trace_id)
      observation = related_trace.observations[0]
      # observations.append(observation)
      observations.append({
        "trace_id": observation.trace_id,
        "input": observation.input,
        "output": observation.output
      })

    return observations


if __name__ == "__main__":
  eval = RunEvaluator()
  results = eval.get_observations_for_eval()
  for i, r in enumerate[Any](results):
    print('\n', '-'*50, i, '-'*50, '\n')
    pprint(r)

