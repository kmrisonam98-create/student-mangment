from pydantic import BaseModel, Field, EmailStr


class student_register_model(BaseModel):
    name: str = Field(description='student name', max_length=15)
    age: int = Field(description='student age')
    grade: str = Field(description='student grade')
    email: EmailStr = Field(description='student email')
    password: str = Field(description='student password')

    @classmethod
    def validate_age(cls, age):
        if age < 0:
            raise ValueError('age cannot be less than zero')
        return age


class student_login_model(BaseModel):
    email: EmailStr
    password: str


class admin_login_model(BaseModel):
    email: EmailStr
    password: str


class attendance_model(BaseModel):
    student_id: int
    date: str
    status: str


class result_model(BaseModel):
    student_id: int
    subject: str
    marks: int
    total_marks: int
