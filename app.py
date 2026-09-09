import streamlit as st
import requests
import pandas as pd
from datetime import date



API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Student Management System",
    page_icon="🎓",
    layout="wide"
)


st.markdown("""
<style>

.main {
    background-color: #f5f7fb;
}

.login-box {
    max-width: 500px;
    margin: auto;
    padding: 30px;
    border-radius: 15px;
    background-color: white;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.10);
}

.dashboard-card {
    padding: 20px;
    border-radius: 15px;
    background-color: white;
    box-shadow: 0px 3px 15px rgba(0,0,0,0.08);
    margin-bottom: 15px;
}

.title {
    font-size: 32px;
    font-weight: bold;
}

.subtitle {
    font-size: 18px;
    color: #666;
}

</style>
""", unsafe_allow_html=True)



if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "role" not in st.session_state:
    st.session_state.role = None

if "student_id" not in st.session_state:
    st.session_state.student_id = None

if "student_name" not in st.session_state:
    st.session_state.student_name = None

if "student_email" not in st.session_state:
    st.session_state.student_email = None



def api_request(method, endpoint, data=None):

    try:
        url = f"{API_URL}{endpoint}"

        if method == "GET":
            response = requests.get(url)

        elif method == "POST":
            response = requests.post(url, json=data)

        elif method == "PUT":
            response = requests.put(url, json=data)

        elif method == "DELETE":
            response = requests.delete(url)

        else:
            st.error("Invalid HTTP method")
            return None

        return response

    except requests.exceptions.ConnectionError:
        st.error(
            "❌ FastAPI server is not running. "
            "Please start api.py first."
        )
        return None



def logout():

    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.student_id = None
    st.session_state.student_name = None
    st.session_state.student_email = None

    st.rerun()



def login_page():

    st.markdown(
        "<h1 style='text-align:center;'>🎓 Student Management System</h1>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<p style='text-align:center;color:gray;'>"
        "Student & Admin Portal"
        "</p>",
        unsafe_allow_html=True
    )

    st.write("")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        st.markdown(
            "<div class='dashboard-card'>",
            unsafe_allow_html=True
        )

        login_type = st.radio(
            "Login As",
            ["👨‍🎓 Student", "👨‍💼 Admin"],
            horizontal=True
        )

        st.divider()

        email = st.text_input(
            "📧 Email",
            placeholder="Enter email"
        )

        password = st.text_input(
            "🔐 Password",
            type="password",
            placeholder="Enter password"
        )

        login_button = st.button(
            "🔐 Login",
            use_container_width=True
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

        if login_button:

            if not email or not password:

                st.warning(
                    "⚠️ Please enter email and password."
                )

                return


            if login_type == "👨‍🎓 Student":

                response = api_request(
                    "POST",
                    "/student_login",
                    {
                        "email": email,
                        "password": password
                    }
                )

                if response is not None:

                    if response.status_code == 200:

                        data = response.json()

                        st.session_state.logged_in = True
                        st.session_state.role = "student"

                        st.session_state.student_id = data[
                            "student_id"
                        ]

                        st.session_state.student_name = data[
                            "name"
                        ]

                        st.session_state.student_email = data[
                            "email"
                        ]

                        st.success(
                            "✅ Student login successful!"
                        )

                        st.rerun()

                    else:

                        try:
                            error = response.json()["detail"]
                        except:
                            error = "Invalid login"

                        st.error(f"❌ {error}")


            else:

                response = api_request(
                    "POST",
                    "/admin_login",
                    {
                        "email": email,
                        "password": password
                    }
                )

                if response is not None:

                    if response.status_code == 200:

                        st.session_state.logged_in = True
                        st.session_state.role = "admin"

                        st.success(
                            "✅ Admin login successful!"
                        )

                        st.rerun()

                    else:

                        try:
                            error = response.json()["detail"]
                        except:
                            error = "Invalid admin login"

                        st.error(f"❌ {error}")




def student_dashboard():

    st.sidebar.title("🎓 Student Panel")

    st.sidebar.write(
        f"👋 **{st.session_state.student_name}**"
    )

    st.sidebar.write(
        f"Student ID: {st.session_state.student_id}"
    )

    menu = st.sidebar.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "👤 My Profile",
            "📅 Attendance",
            "📊 Results"
        ]
    )

    st.sidebar.divider()

    if st.sidebar.button(
        "🚪 Logout",
        use_container_width=True
    ):
        logout()

    student_id = st.session_state.student_id

    

    if menu == "🏠 Dashboard":

        st.title(
            f"👋 Welcome, {st.session_state.student_name}"
        )

        st.caption(
            f"Student ID: {student_id}"
        )

        st.divider()

        col1, col2, col3 = st.columns(3)

        
        response = api_request(
            "GET",
            f"/attendance_percentage/{student_id}"
        )

        attendance = None

        if response is not None and response.status_code == 200:
            attendance = response.json()

        
        response2 = api_request(
            "GET",
            f"/overall_result/{student_id}"
        )

        result = None

        if response2 is not None and response2.status_code == 200:
            result = response2.json()

        with col1:

            st.metric(
                "📅 Attendance",
                f"{attendance['attendance_percentage']}%"
                if attendance
                else "N/A"
            )

        with col2:

            st.metric(
                "📊 Result",
                f"{result['overall_percentage']}%"
                if result
                else "N/A"
            )

        with col3:

            st.metric(
                "🏆 Grade",
                result["overall_grade"]
                if result
                else "N/A"
            )

        st.write("")

        st.info(
            "Use the sidebar to view your profile, "
            "attendance and results."
        )


    elif menu == "👤 My Profile":

        st.title("👤 My Profile")

        response = api_request(
            "GET",
            f"/students/{student_id}"
        )

        if response is not None:

            if response.status_code == 200:

                student = response.json()

                col1, col2 = st.columns(2)

                with col1:

                    st.markdown(
                        "<div class='dashboard-card'>",
                        unsafe_allow_html=True
                    )

                    st.subheader("Student Information")

                    st.write(
                        f"**Student ID:** {student['id']}"
                    )

                    st.write(
                        f"**Name:** {student['name']}"
                    )

                    st.write(
                        f"**Age:** {student['age']}"
                    )

                    st.write(
                        f"**Grade:** {student['grade']}"
                    )

                    st.write(
                        f"**Email:** {student['email']}"
                    )

                    st.markdown(
                        "</div>",
                        unsafe_allow_html=True
                    )

            else:

                st.error("Student information not found.")



    elif menu == "📅 Attendance":

        st.title("📅 My Attendance")

        response = api_request(
            "GET",
            f"/attendance/{student_id}"
        )

        response2 = api_request(
            "GET",
            f"/attendance_percentage/{student_id}"
        )

        if response2 is not None and response2.status_code == 200:

            attendance_summary = response2.json()

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Total Classes",
                    attendance_summary["total_classes"]
                )

            with col2:
                st.metric(
                    "Present",
                    attendance_summary["present"]
                )

            with col3:
                st.metric(
                    "Absent",
                    attendance_summary["absent"]
                )

            with col4:
                st.metric(
                    "Attendance",
                    f"{attendance_summary['attendance_percentage']}%"
                )

        st.divider()

        if response is not None and response.status_code == 200:

            attendance_data = response.json()

            df = pd.DataFrame(attendance_data)

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info("No attendance record found.")


    elif menu == "📊 Results":

        st.title("📊 My Results")

        response = api_request(
            "GET",
            f"/results/{student_id}"
        )

        response2 = api_request(
            "GET",
            f"/overall_result/{student_id}"
        )

        if response2 is not None and response2.status_code == 200:

            result_summary = response2.json()

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Total Marks",
                    result_summary["total_mark_obtained"]
                )

            with col2:
                st.metric(
                    "Percentage",
                    f"{result_summary['overall_percentage']}%"
                )

            with col3:
                st.metric(
                    "Overall Grade",
                    result_summary["overall_grade"]
                )

        st.divider()

        if response is not None and response.status_code == 200:

            results = response.json()

            df = pd.DataFrame(results)

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info("No result found.")




def admin_dashboard():

    st.sidebar.title("👨‍💼 Admin Panel")

    menu = st.sidebar.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "➕ Add Student",
            "👥 All Students",
            "🔎 Search Student",
            "🎓 Filter by Grade",
            "✏️ Update Student",
            "🗑️ Delete Student",
            "📅 Mark Attendance",
            "📊 Add Result"
        ]
    )

    st.sidebar.divider()

    if st.sidebar.button(
        "🚪 Logout",
        use_container_width=True
    ):
        logout()

    

    if menu == "🏠 Dashboard":

        st.title("👨‍💼 Admin Dashboard")

        response = api_request(
            "GET",
            "/students"
        )

        if response is not None and response.status_code == 200:

            students = response.json()

            total_students = len(students)

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "👥 Total Students",
                    total_students
                )

            with col2:

                grades = set()

                for student in students:
                    grades.add(student["grade"])

                st.metric(
                    "🎓 Total Grades",
                    len(grades)
                )

            with col3:

                st.metric(
                    "📚 System Status",
                    "Online"
                )

        st.divider()

        st.info(
            "Use the sidebar to manage students, "
            "attendance and results."
        )

    

    elif menu == "➕ Add Student":

        st.title("➕ Add New Student")

        with st.form("add_student_form"):

            name = st.text_input("Student Name")

            col1, col2 = st.columns(2)

            with col1:
                age = st.number_input(
                    "Age",
                    min_value=1,
                    max_value=100,
                    value=18
                )

            with col2:
                grade = st.text_input(
                    "Grade",
                    placeholder="e.g. A"
                )

            email = st.text_input(
                "Email"
            )

            password = st.text_input(
                "Password",
                type="password"
            )

            submit = st.form_submit_button(
                "➕ Add Student",
                use_container_width=True
            )

        if submit:

            if not name or not grade or not email or not password:

                st.warning(
                    "⚠️ Please fill all fields."
                )

            else:

                response = api_request(
                    "POST",
                    "/add_student",
                    {
                        "name": name,
                        "age": age,
                        "grade": grade,
                        "email": email,
                        "password": password
                    }
                )

                if response is not None:

                    if response.status_code == 200:

                        st.success(
                            "✅ Student added successfully!"
                        )

                    else:

                        try:
                            st.error(
                                response.json()["detail"]
                            )
                        except:
                            st.error(
                                "Unable to add student."
                            )

    

    elif menu == "👥 All Students":

        st.title("👥 All Students")

        response = api_request(
            "GET",
            "/students"
        )

        if response is not None and response.status_code == 200:

            students = response.json()

            if students:

                df = pd.DataFrame(students)

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.info("No students found.")

    

    elif menu == "🔎 Search Student":

        st.title("🔎 Search Student")

        name = st.text_input(
            "Enter student name"
        )

        if st.button(
            "🔎 Search",
            use_container_width=True
        ):

            if not name:

                st.warning(
                    "Please enter a student name."
                )

            else:

                response = api_request(
                    "GET",
                    f"/search_student?name={name}"
                )

                if response is not None:

                    if response.status_code == 200:

                        students = response.json()

                        df = pd.DataFrame(students)

                        st.dataframe(
                            df,
                            use_container_width=True,
                            hide_index=True
                        )

                    else:

                        st.error(
                            "❌ Student not found."
                        )

    

    elif menu == "🎓 Filter by Grade":

        st.title("🎓 Filter Students by Grade")

        grade = st.text_input(
            "Enter Grade",
            placeholder="e.g. A"
        )

        if st.button(
            "🔎 Filter",
            use_container_width=True
        ):

            response = api_request(
                "GET",
                f"/students/grade/{grade}"
            )

            if response is not None:

                if response.status_code == 200:

                    students = response.json()

                    df = pd.DataFrame(students)

                    st.dataframe(
                        df,
                        use_container_width=True,
                        hide_index=True
                    )

                else:

                    st.error(
                        "No students found for this grade."
                    )

    

    elif menu == "✏️ Update Student":

        st.title("✏️ Update Student")

        student_id = st.number_input(
            "Student ID",
            min_value=1,
            step=1
        )

        if st.button(
            "Load Student",
            use_container_width=True
        ):

            response = api_request(
                "GET",
                f"/students/{student_id}"
            )

            if response is not None and response.status_code == 200:

                student = response.json()

                st.session_state.update_student = student

            else:

                st.error("Student not found.")

        if "update_student" in st.session_state:

            student = st.session_state.update_student

            with st.form("update_form"):

                name = st.text_input(
                    "Name",
                    value=student["name"]
                )

                age = st.number_input(
                    "Age",
                    min_value=1,
                    max_value=100,
                    value=student["age"]
                )

                grade = st.text_input(
                    "Grade",
                    value=student["grade"]
                )

                email = st.text_input(
                    "Email",
                    value=student["email"]
                )

                update = st.form_submit_button(
                    "💾 Update Student",
                    use_container_width=True
                )

            if update:

                response = api_request(
                    "PUT",
                    f"/students/{student_id}",
                    {
                        "name": name,
                        "age": age,
                        "grade": grade,
                        "email": email,
                        "password": ""
                    }
                )

                if response is not None:

                    if response.status_code == 200:

                        st.success(
                            "✅ Student updated successfully!"
                        )

                        del st.session_state.update_student

                    else:

                        st.error(
                            "Unable to update student."
                        )

    

    elif menu == "🗑️ Delete Student":

        st.title("🗑️ Delete Student")

        student_id = st.number_input(
            "Student ID",
            min_value=1,
            step=1
        )

        confirm = st.checkbox(
            "I confirm that I want to delete this student."
        )

        if st.button(
            "🗑️ Delete Student",
            use_container_width=True
        ):

            if not confirm:

                st.warning(
                    "Please confirm deletion."
                )

            else:

                response = api_request(
                    "DELETE",
                    f"/students/{student_id}"
                )

                if response is not None:

                    if response.status_code == 200:

                        st.success(
                            "✅ Student deleted successfully!"
                        )

                    else:

                        try:
                            st.error(
                                response.json()["detail"]
                            )
                        except:
                            st.error(
                                "Student could not be deleted."
                            )

    

    elif menu == "📅 Mark Attendance":

        st.title("📅 Mark Attendance")

        with st.form("attendance_form"):

            student_id = st.number_input(
                "Student ID",
                min_value=1,
                step=1
            )

            attendance_date = st.date_input(
                "Date",
                value=date.today()
            )

            status = st.selectbox(
                "Status",
                [
                    "Present",
                    "Absent"
                ]
            )

            submit = st.form_submit_button(
                "📅 Mark Attendance",
                use_container_width=True
            )

        if submit:

            response = api_request(
                "POST",
                "/attendance",
                {
                    "student_id": student_id,
                    "date": str(attendance_date),
                    "status": status
                }
            )

            if response is not None:

                if response.status_code == 200:

                    st.success(
                        "✅ Attendance marked successfully!"
                    )

                else:

                    try:
                        st.error(
                            response.json()["detail"]
                        )
                    except:
                        st.error(
                            "Unable to mark attendance."
                        )


    elif menu == "📊 Add Result":

        st.title("📊 Add Student Result")

        with st.form("result_form"):

            student_id = st.number_input(
                "Student ID",
                min_value=1,
                step=1
            )

            subject = st.text_input(
                "Subject"
            )

            col1, col2 = st.columns(2)

            with col1:

                marks = st.number_input(
                    "Marks Obtained",
                    min_value=0,
                    step=1
                )

            with col2:

                total_marks = st.number_input(
                    "Total Marks",
                    min_value=1,
                    step=1,
                    value=100
                )

            submit = st.form_submit_button(
                "📊 Add Result",
                use_container_width=True
            )

        if submit:

            if not subject:

                st.warning(
                    "Please enter subject."
                )

            elif marks > total_marks:

                st.error(
                    "Marks cannot be greater than total marks."
                )

            else:

                response = api_request(
                    "POST",
                    "/results",
                    {
                        "student_id": student_id,
                        "subject": subject,
                        "marks": marks,
                        "total_marks": total_marks
                    }
                )

                if response is not None:

                    if response.status_code == 200:

                        st.success(
                            "✅ Result added successfully!"
                        )

                    else:

                        try:
                            st.error(
                                response.json()["detail"]
                            )
                        except:
                            st.error(
                                "Unable to add result."
                            )

if not st.session_state.logged_in:

    login_page()

else:

    if st.session_state.role == "student":

        student_dashboard()

    elif st.session_state.role == "admin":

        admin_dashboard()