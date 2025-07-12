from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List, Dict
from uuid import UUID
from collections import defaultdict

from models.contact import Contact, ContactCreate, ContactUpdate
from models.customer import Customer, CustomerCreate, CustomerUpdate, CustomerStatus
from models.opportunity import Opportunity, OpportunityCreate, OpportunityUpdate, OpportunityStage
from models.activity import Activity, ActivityCreate, ActivityUpdate
from models.note import Note, NoteCreate, NoteUpdate
from models.user import User, UserCreate, UserUpdate

from service import contacts, customers, opportunities, activities, notes, users
from service.redis_manager import redis_manager

app = FastAPI(title="CRM System API")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """
    Render the dashboard with customer and opportunity data.
    """
    # Get all customers
    all_customers = customers.get_customers()

    # Get all opportunities
    all_opportunities = opportunities.get_opportunities()

    # Calculate customer statistics
    total_customers = len(all_customers)
    customer_status_counts = defaultdict(int)
    for customer in all_customers:
        customer_status_counts[customer.status] = customer_status_counts[customer.status] + 1

    # Calculate opportunity statistics
    total_opportunities = len(all_opportunities)
    total_opportunity_value = sum(opp.amount or 0 for opp in all_opportunities)

    # Calculate win rate
    closed_opportunities = [opp for opp in all_opportunities if opp.stage in [OpportunityStage.CLOSED_WON, OpportunityStage.CLOSED_LOST]]
    won_opportunities = [opp for opp in all_opportunities if opp.stage == OpportunityStage.CLOSED_WON]
    win_rate = round((len(won_opportunities) / len(closed_opportunities) * 100) if closed_opportunities else 0)

    # Calculate opportunity stage data
    opportunity_stage_data = defaultdict(lambda: {"count": 0, "value": 0})
    for opp in all_opportunities:
        opportunity_stage_data[opp.stage]["count"] += 1
        opportunity_stage_data[opp.stage]["value"] += opp.amount or 0

    # Format opportunity stage data for display
    for stage, data in opportunity_stage_data.items():
        data["value"] = round(data["value"], 2)

    # Prepare data for pie charts
    opportunity_stage_labels = [stage.value.replace('_', ' ').capitalize() for stage in OpportunityStage]
    opportunity_stage_counts = [opportunity_stage_data[stage]["count"] for stage in OpportunityStage]

    customer_status_labels = [status.value.capitalize() for status in CustomerStatus]
    customer_status_counts_list = [customer_status_counts[status] for status in CustomerStatus]

    # Get recent customers and opportunities
    recent_customers = sorted(all_customers, key=lambda x: x.id)[:5]  # In a real app, sort by creation date
    recent_opportunities = sorted(all_opportunities, key=lambda x: x.id)[:5]  # In a real app, sort by creation date

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "total_customers": total_customers,
        "total_opportunities": total_opportunities,
        "total_opportunity_value": round(total_opportunity_value, 2),
        "win_rate": win_rate,
        "customer_status_counts": dict(customer_status_counts),
        "opportunity_stage_data": dict(opportunity_stage_data),
        "opportunity_stage_labels": opportunity_stage_labels,
        "opportunity_stage_counts": opportunity_stage_counts,
        "customer_status_labels": customer_status_labels,
        "customer_status_counts_list": customer_status_counts_list,
        "recent_customers": recent_customers,
        "recent_opportunities": recent_opportunities
    })


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/contacts", response_model=List[Contact])
async def list_contacts():
    """
    Get all contacts.
    """
    return contacts.get_contacts()


@app.get("/contacts/{contact_id}", response_model=Contact)
async def get_contact(contact_id: UUID):
    """
    Get a specific contact by ID.
    """
    contact = contacts.get_contact(contact_id)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@app.post("/contacts", response_model=Contact, status_code=201)
async def create_contact(contact: ContactCreate):
    """
    Create a new contact.
    """
    return contacts.create_contact(contact)


@app.put("/contacts/{contact_id}", response_model=Contact)
async def update_contact(contact_id: UUID, contact_update: ContactUpdate):
    """
    Update an existing contact.
    """
    updated_contact = contacts.update_contact(contact_id, contact_update)
    if updated_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return updated_contact


@app.delete("/contacts/{contact_id}", status_code=204)
async def delete_contact(contact_id: UUID):
    """
    Delete a contact.
    """
    success = contacts.delete_contact(contact_id)
    if not success:
        raise HTTPException(status_code=404, detail="Contact not found")
    return None


# Customer endpoints
@app.get("/customers", response_model=List[Customer])
async def list_customers():
    """
    Get all customers.
    """
    return customers.get_customers()


@app.get("/customers/{customer_id}", response_model=Customer)
async def get_customer(customer_id: UUID):
    """
    Get a specific customer by ID.
    """
    customer = customers.get_customer(customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@app.post("/customers", response_model=Customer, status_code=201)
async def create_customer(customer: CustomerCreate):
    """
    Create a new customer.
    """
    return customers.create_customer(customer)


@app.put("/customers/{customer_id}", response_model=Customer)
async def update_customer(customer_id: UUID, customer_update: CustomerUpdate):
    """
    Update an existing customer.
    """
    updated_customer = customers.update_customer(customer_id, customer_update)
    if updated_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return updated_customer


@app.delete("/customers/{customer_id}", status_code=204)
async def delete_customer(customer_id: UUID):
    """
    Delete a customer.
    """
    success = customers.delete_customer(customer_id)
    if not success:
        raise HTTPException(status_code=404, detail="Customer not found")
    return None


# Opportunity endpoints
@app.get("/opportunities", response_model=List[Opportunity])
async def list_opportunities():
    """
    Get all opportunities.
    """
    return opportunities.get_opportunities()


@app.get("/opportunities/{opportunity_id}", response_model=Opportunity)
async def get_opportunity(opportunity_id: UUID):
    """
    Get a specific opportunity by ID.
    """
    opportunity = opportunities.get_opportunity(opportunity_id)
    if opportunity is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return opportunity


@app.get("/customers/{customer_id}/opportunities", response_model=List[Opportunity])
async def list_customer_opportunities(customer_id: UUID):
    """
    Get all opportunities for a specific customer.
    """
    customer = customers.get_customer(customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return opportunities.get_opportunities_by_customer(customer_id)


@app.post("/opportunities", response_model=Opportunity, status_code=201)
async def create_opportunity(opportunity: OpportunityCreate):
    """
    Create a new opportunity.
    """
    # Verify that the customer exists
    customer = customers.get_customer(opportunity.customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    return opportunities.create_opportunity(opportunity)


@app.put("/opportunities/{opportunity_id}", response_model=Opportunity)
async def update_opportunity(opportunity_id: UUID, opportunity_update: OpportunityUpdate):
    """
    Update an existing opportunity.
    """
    # If customer_id is being updated, verify that the customer exists
    if opportunity_update.customer_id is not None:
        customer = customers.get_customer(opportunity_update.customer_id)
        if customer is None:
            raise HTTPException(status_code=404, detail="Customer not found")

    updated_opportunity = opportunities.update_opportunity(opportunity_id, opportunity_update)
    if updated_opportunity is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return updated_opportunity


@app.delete("/opportunities/{opportunity_id}", status_code=204)
async def delete_opportunity(opportunity_id: UUID):
    """
    Delete an opportunity.
    """
    success = opportunities.delete_opportunity(opportunity_id)
    if not success:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return None


# Activity endpoints
@app.get("/activities", response_model=List[Activity])
async def list_activities():
    """
    Get all activities.
    """
    return activities.get_activities()


@app.get("/activities/{activity_id}", response_model=Activity)
async def get_activity(activity_id: UUID):
    """
    Get a specific activity by ID.
    """
    activity = activities.get_activity(activity_id)
    if activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity


@app.get("/customers/{customer_id}/activities", response_model=List[Activity])
async def list_customer_activities(customer_id: UUID):
    """
    Get all activities for a specific customer.
    """
    customer = customers.get_customer(customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return activities.get_activities_by_customer(customer_id)


@app.get("/opportunities/{opportunity_id}/activities", response_model=List[Activity])
async def list_opportunity_activities(opportunity_id: UUID):
    """
    Get all activities for a specific opportunity.
    """
    opportunity = opportunities.get_opportunity(opportunity_id)
    if opportunity is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return activities.get_activities_by_opportunity(opportunity_id)


@app.post("/activities", response_model=Activity, status_code=201)
async def create_activity(activity: ActivityCreate):
    """
    Create a new activity.
    """
    # Verify that the customer exists if customer_id is provided
    if activity.customer_id is not None:
        customer = customers.get_customer(activity.customer_id)
        if customer is None:
            raise HTTPException(status_code=404, detail="Customer not found")

    # Verify that the opportunity exists if opportunity_id is provided
    if activity.opportunity_id is not None:
        opportunity = opportunities.get_opportunity(activity.opportunity_id)
        if opportunity is None:
            raise HTTPException(status_code=404, detail="Opportunity not found")

    return activities.create_activity(activity)


@app.put("/activities/{activity_id}", response_model=Activity)
async def update_activity(activity_id: UUID, activity_update: ActivityUpdate):
    """
    Update an existing activity.
    """
    # If customer_id is being updated, verify that the customer exists
    if activity_update.customer_id is not None:
        customer = customers.get_customer(activity_update.customer_id)
        if customer is None:
            raise HTTPException(status_code=404, detail="Customer not found")

    # If opportunity_id is being updated, verify that the opportunity exists
    if activity_update.opportunity_id is not None:
        opportunity = opportunities.get_opportunity(activity_update.opportunity_id)
        if opportunity is None:
            raise HTTPException(status_code=404, detail="Opportunity not found")

    updated_activity = activities.update_activity(activity_id, activity_update)
    if updated_activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")
    return updated_activity


@app.delete("/activities/{activity_id}", status_code=204)
async def delete_activity(activity_id: UUID):
    """
    Delete an activity.
    """
    success = activities.delete_activity(activity_id)
    if not success:
        raise HTTPException(status_code=404, detail="Activity not found")
    return None


# Note endpoints
@app.get("/notes", response_model=List[Note])
async def list_notes():
    """
    Get all notes.
    """
    return notes.get_notes()


@app.get("/notes/{note_id}", response_model=Note)
async def get_note(note_id: UUID):
    """
    Get a specific note by ID.
    """
    note = notes.get_note(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@app.get("/customers/{customer_id}/notes", response_model=List[Note])
async def list_customer_notes(customer_id: UUID):
    """
    Get all notes for a specific customer.
    """
    customer = customers.get_customer(customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return notes.get_notes_by_customer(customer_id)


@app.get("/opportunities/{opportunity_id}/notes", response_model=List[Note])
async def list_opportunity_notes(opportunity_id: UUID):
    """
    Get all notes for a specific opportunity.
    """
    opportunity = opportunities.get_opportunity(opportunity_id)
    if opportunity is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return notes.get_notes_by_opportunity(opportunity_id)


@app.get("/activities/{activity_id}/notes", response_model=List[Note])
async def list_activity_notes(activity_id: UUID):
    """
    Get all notes for a specific activity.
    """
    activity = activities.get_activity(activity_id)
    if activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")
    return notes.get_notes_by_activity(activity_id)


@app.post("/notes", response_model=Note, status_code=201)
async def create_note(note: NoteCreate):
    """
    Create a new note.
    """
    # Verify that the customer exists if customer_id is provided
    if note.customer_id is not None:
        customer = customers.get_customer(note.customer_id)
        if customer is None:
            raise HTTPException(status_code=404, detail="Customer not found")

    # Verify that the opportunity exists if opportunity_id is provided
    if note.opportunity_id is not None:
        opportunity = opportunities.get_opportunity(note.opportunity_id)
        if opportunity is None:
            raise HTTPException(status_code=404, detail="Opportunity not found")

    # Verify that the activity exists if activity_id is provided
    if note.activity_id is not None:
        activity = activities.get_activity(note.activity_id)
        if activity is None:
            raise HTTPException(status_code=404, detail="Activity not found")

    return notes.create_note(note)


@app.put("/notes/{note_id}", response_model=Note)
async def update_note(note_id: UUID, note_update: NoteUpdate):
    """
    Update an existing note.
    """
    # If customer_id is being updated, verify that the customer exists
    if note_update.customer_id is not None:
        customer = customers.get_customer(note_update.customer_id)
        if customer is None:
            raise HTTPException(status_code=404, detail="Customer not found")

    # If opportunity_id is being updated, verify that the opportunity exists
    if note_update.opportunity_id is not None:
        opportunity = opportunities.get_opportunity(note_update.opportunity_id)
        if opportunity is None:
            raise HTTPException(status_code=404, detail="Opportunity not found")

    # If activity_id is being updated, verify that the activity exists
    if note_update.activity_id is not None:
        activity = activities.get_activity(note_update.activity_id)
        if activity is None:
            raise HTTPException(status_code=404, detail="Activity not found")

    updated_note = notes.update_note(note_id, note_update)
    if updated_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return updated_note


@app.delete("/notes/{note_id}", status_code=204)
async def delete_note(note_id: UUID):
    """
    Delete a note.
    """
    success = notes.delete_note(note_id)
    if not success:
        raise HTTPException(status_code=404, detail="Note not found")
    return None


# User endpoints
@app.get("/users", response_model=List[User])
async def list_users():
    """
    Get all users.
    """
    return users.get_users()


@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: UUID):
    """
    Get a specific user by ID.
    """
    user = users.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/users/by-username/{username}", response_model=User)
async def get_user_by_username(username: str):
    """
    Get a user by username.
    """
    user = users.get_user_by_username(username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/users", response_model=User, status_code=201)
async def create_user(user: UserCreate):
    """
    Create a new user.
    """
    try:
        return users.create_user(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: UUID, user_update: UserUpdate):
    """
    Update an existing user.
    """
    try:
        updated_user = users.update_user(user_id, user_update)
        if updated_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: UUID):
    """
    Delete a user.
    """
    success = users.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return None


@app.post("/login")
async def login(username: str, password: str):
    """
    Authenticate a user.
    """
    user = users.authenticate_user(username, password)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"message": "Login successful", "user": user}
