from flask import Flask, request, render_template
import psycopg2

app = Flask(__name__)

# Connect to database, run one query and return the rows
def run(sql, values = (), fetch = False):
    con = psycopg2.connect(dbname = 'results', user = 'postgres', password = 'root', host = 'localhost', port = '5432')
    cur = con.cursor()
    cur.execute(sql, values)
    rows = cur.fetchall() if fetch else None
    con.commit()
    con.close()
    return rows

# Create tables
def create_table():
    run("""CREATE TABLE IF NOT EXISTS Students(roll_no INT PRIMARY KEY, name VARCHAR(100),
        email VARCHAR(100) UNIQUE, phone VARCHAR(10), password VARCHAR(100));
        CREATE TABLE IF NOT EXISTS Results(result_id SERIAL PRIMARY KEY, roll_no INT,
        subject VARCHAR(50), marks INT)""")

    # Sample results 
    if run("SELECT COUNT(*) FROM Results", fetch = True)[0][0] == 0:
        run("""INSERT INTO Results (roll_no, subject, marks) VALUES
             (1, 'FSD', 85), (1, 'Java', 78), (1, 'DS', 90), (1, 'Web Development', 88),(1, 'Cloud', 88),
            (2, 'FSD', 65), (2, 'Java', 58), (2, 'DS', 70), (2, 'Web Development', 62),(2, 'Cloud', 76),
            (3, 'FSD', 35), (3, 'Java', 60), (3, 'DS', 42), (3, 'Web Development', 55),(3, 'Cloud', 68),
            (4, 'FSD', 65), (4, 'Java', 67), (4, 'DS', 32), (4, 'Web Development', 58),(4, 'Cloud', 53),
            (5, 'FSD', 78), (5, 'Java', 90), (5, 'DS', 52), (5, 'Web Development', 89),(5, 'Cloud', 568)
            """)

# Get result of the student and show dashboard
def show_dashboard(roll_no, name):
    results = run("SELECT subject, marks FROM Results WHERE roll_no = %s", (roll_no,), fetch = True)

    total = 0
    final = "PASS"
    for r in results:
        total = total + r[1]
        if r[1] < 40:                
            final = "FAIL"

    percentage = round(total / max(len(results), 1), 2)

    return render_template("dashboard.html", name = name, roll_no = roll_no, results = results,
                           total = total, max_total = len(results) * 100, percentage = percentage, final = final)

# Registration 
@app.route("/", methods = ['GET', 'POST'])
def register():
    msg = ""

    if request.method == "POST":
        roll_no = request.form['roll_no'].strip()
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        phone = request.form['phone'].strip()
        password = request.form['password'].strip()
        confirm = request.form['confirm'].strip()

        if "" in (roll_no, name, email, phone, password, confirm):
            msg = "Please fill in all fields."
        elif not roll_no.isdigit() or not phone.isdigit() or len(phone) != 10:
            msg = "Roll No must be a number and Phone must be 10 digits."
        elif len(password) < 6 or password != confirm:
            msg = "Password must be 6+ characters and match Confirm Password."
        elif run("SELECT * FROM Students WHERE email = %s OR roll_no = %s", (email, roll_no), fetch = True):
            msg = "Email or Roll number already registered."
        else:
            run("INSERT INTO Students (roll_no, name, email, phone, password) VALUES(%s,%s,%s,%s,%s)",
                (roll_no, name, email, phone, password))
            return show_dashboard(int(roll_no), name)

    return render_template("register.html", msg = msg)

# Login (dashboard is shown after successful login)
@app.route("/login", methods = ['GET', 'POST'])
def login():
    msg = ""

    if request.method == "POST":
        email = request.form['email'].strip()
        password = request.form['password'].strip()

        student = run("SELECT roll_no, name FROM Students WHERE email = %s AND password = %s",
                      (email, password), fetch = True)
        if student:
            return show_dashboard(student[0][0], student[0][1])
        msg = "Invalid email or password."

    return render_template("login.html", msg = msg)

# Logout
@app.route("/logout")
def logout():
    return render_template("login.html", msg = "You have been logged out.")

if __name__ == '__main__':
    create_table()
    app.run(debug = True)
