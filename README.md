# 🎓 Mindwhile ERP - Developer Guide & Documentation

Welcome to the Mindwhile ERP project! 👋

This documentation is designed to help you understand, run, and contribute to this **Multi-Tenant School Management System**. Whether you are a fresher or an experienced developer, this guide will walk you through the architecture, structure, and how to add new features.

---

## 🏗️ What is this Project?

Imagine an apartment complex.
- **The Building** is the software (Mindwhile ERP).
- **The Apartments** are the Schools (Tenants).
- **The Landlord** is the Super Admin.

Each apartment (School) has its own keys, furniture, and rooms. They don't share anything with their neighbors.
In technical terms: **Every school has its own separate database.** This is called **Database-per-Tenant Multi-Tenancy**.

### Key Technologies
- **Python 3.12+**: The programming language.
- **FastAPI**: The web framework (fast, async, modern).
- **MySQL**: The database (stores data).
- **Redis**: The cache (makes things fast).
- **Docker** (Optional): Containerization.

---

## 📐 Architecture Explained (Simply)

When a user visits `school-a.erp.com`, here is what happens:

1.  **Reception (Middleware)**: The app sees the request comes from `school-a`.
2.  **Directory (Tenant Resolution)**: It checks a "Directory" (Redis Cache) to find `school-a`'s database credentials.
3.  **Connection (Manager)**: It opens a connection *specifically* to `school-a`'s database.
4.  **Service**: The code runs (gets students, marks attendance, etc.) using that connection.
5.  **Response**: Data is sent back.

**Result**: `School A` can never see `School B`'s data because they are in completely different databases!

---

## 📂 Project Structure (Where is everything?)

Understanding the folder structure is key to contributing.

```bash
mindwhile-erp-fastapi/
├── app/
│   ├── main.py                # 🏁 The entry point. Starts the app.
│   ├── config.py              # ⚙️ Settings (DB URLs, Secret Keys).
│   │
│   ├── modules/               # 📦 BUSINESS LOGIC (Where you will work most!)
│   │   ├── auth/              # Login, Logout logic.
│   │   ├── students/          # Student management.
│   │   ├── teachers/          # Teacher management.
│   │   └── ...
│   │
│   ├── tenancy/               # 🏘️ The Engine Room (Don't touch unless you know what you're doing)
│   │   ├── database.py        # Gives you the correct DB session.
│   │   ├── middleware.py      # Figures out which school is calling.
│   │   └── manager.py         # Manages DB connections.
│   │
│   └── rbac/                  # 🛡️ Permissions (Who can do what?)
│       └── decorators.py      # @require_permissions()
│
├── scripts/                   # 🛠️ Tools
│   ├── provision_tenant.py    # Script to create a NEW school.
│   └── generate_key.py        # Helper to make secure keys.
│
├── alembic_master/            # 🗄️ Migrations for the "Landlord" DB (Global data).
└── alembic_tenant/            # 🗄️ Migrations for "Apartment" DBs (School data).
```

---

## 👩‍💻 Developer Cookbook

### 1. How to Run the App?
See [SETUP_GUIDE.md](./SETUP_GUIDE.md) for detailed installation steps.

### 2. How to Add a New API?

Let's say you want to add a feature to **"List all Library Books"**.

**Step 1: Create the Model (The Table)**
Go to `app/modules/library/models.py`:
```python
from sqlalchemy import Column, String, Integer
from app.tenancy.models import TenantBase

class Book(TenantBase):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    author = Column(String(255))
```

**Step 2: Create the Schema (The Data Shape)**
Go to `app/modules/library/schemas.py`:
```python
from pydantic import BaseModel

class BookCreate(BaseModel):
    title: str
    author: str
```

**Step 3: Create the Router (The Endpoint)**
Go to `app/modules/library/router.py`:
```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.tenancy.database import get_tenant_db
from app.modules.library import schemas, models

router = APIRouter()

@router.post("/")
async def add_book(book: schemas.BookCreate, db: AsyncSession = Depends(get_tenant_db)):
    new_book = models.Book(**book.model_dump())
    db.add(new_book)
    await db.commit()
    return {"message": "Book added!"}
```

**Step 4: Register the Router**
Go to `app/main.py` and add:
```python
from app.modules.library.router import router as library_router
app.include_router(library_router, prefix="/api/v1/library", tags=["Library"])
```

### 3. How to Run Migrations?
Since we have many databases, migration is a bit different.

- **For the Master DB (Landlord)**:
  `alembic -c alembic_master.ini upgrade head`

- **For a School DB (Tenant)**:
  `TENANT_DB_NAME=school_a_db alembic -c alembic_tenant.ini upgrade head`

---

## 🤝 Contribution Guidelines

We welcome contributions! Here is how to do it right:

1.  **Branch Naming**:
    - `feature/add-library-module`
    - `fix/login-error`
    - `docs/update-readme`

2.  **Code Style**:
    - Use variables that explain *what* they are (e.g., `student_list` not `sl`).
    - Add comments for complex logic.
    - We use `ruff` or `black` for formatting.

3.  **Pull Request Process**:
    - Explain *what* you changed.
    - Attach a screenshot if it's a UI change.
    - Mention which issue you fixed (e.g., "Fixes #123").

---

## 🆘 Need Help?

- **Database Issues?** Check if MySQL is running.
- **Connection Refused?** Check if Redis is running.
- **"Tenant Not Found"?** Make sure you passed the Header `X-Tenant-Subdomain: yourschool`.

Happy Coding! 🚀
