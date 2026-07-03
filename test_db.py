from database import *

init_db()

save_result(
    "Christy",
    20,
    "Silver",
    "Good performance"
)

print(get_leaderboard())