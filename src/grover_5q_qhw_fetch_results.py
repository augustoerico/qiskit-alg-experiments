from os import environ

from qiskit.primitives.containers.primitive_result import PrimitiveResult
from qiskit_ibm_runtime import QiskitRuntimeService

from utils import write_job_results_json, write_results_csv

def main():
    api_token = environ.get('API_TOKEN')

    runtime_service = QiskitRuntimeService(
        channel='ibm_quantum',
        instance='ibm-q/open/main',
        token=api_token
    )
    job_id = 'cvecm898w2g0008edp90'
    job_result: PrimitiveResult = runtime_service.job(job_id).result()

    pub_result = job_result[0].data.c0.get_counts()

    write_job_results_json(pub_result, 'grover-5q-qhw')
    write_results_csv(pub_result, 'grover-5q-qhw')


if __name__ == '__main__':
    main()
