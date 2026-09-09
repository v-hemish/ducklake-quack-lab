import duckdb
import threading

con = duckdb.connect()

con.execute("INSTALL quack")
con.execute("LOAD quack")

result = con.execute("""
CALL quack_serve(
    'quack:0.0.0.0:9494',
    token = 'ducklake-local-secret',
    allow_other_hostname => true
)
""").fetchall()

print("Quack started:", result, flush=True)

# Keep process alive
threading.Event().wait()
