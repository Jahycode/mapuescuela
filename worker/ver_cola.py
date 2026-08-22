from flowable_client import listar_jobs

jobs = listar_jobs()

print(f"{len(jobs)} trabajos esperando")
for job in jobs:
    dueno = job["lockOwner"] or "libre"
    print(f"  {job['elementName']:28} {dueno}")
