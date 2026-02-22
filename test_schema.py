from app.modules.super_admin.schemas import SuperAdminUpdateRequest
try:
    obj = SuperAdminUpdateRequest(
        full_name="Venkat Reddy",
        phone="9182387725",
        position="Super Admin",
        location="",
        state="",
        pin="",
        zip="",
        tax_no="",
        facebook_url="https://github.com/vnrtumu",
        twitter_url="https://github.com/vnrtumu",
        github_url="https://github.com/vnrtumu",
        dribbble_url="https://github.com/vnrtumu",
    )
    print("Schema is valid!")
except Exception as e:
    print(f"Validation Error: {e}")
