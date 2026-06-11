from app.core.database import SessionLocal
from app.repositories.algorithm_repo import AlgorithmRepository

db = SessionLocal()
repo = AlgorithmRepository()

algo = repo.get_by_name(db, "ML-KEM-512")

print(algo.id)
print(algo.name)
print(algo.type)
print(algo.status)
#algorithms = repo.get_all(db)

#for algo in algorithms:
 #   print(algo.id)
  #  print(algo.name)
   # print(algo.type)
    #print(algo.status)
    #print("------")