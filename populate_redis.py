import random
from uuid import uuid4
from faker import Faker
import redis
from datetime import datetime, timedelta
from models.customer import Customer, CustomerStatus
from models.contact import Contact
from models.opportunity import Opportunity, OpportunityStage
from service.redis_manager import redis_manager

# Initialize Faker for generating random data
fake = Faker()

# Model types for Redis keys
CUSTOMER_MODEL_TYPE = "customer"
CONTACT_MODEL_TYPE = "contact"
OPPORTUNITY_MODEL_TYPE = "opportunity"

def create_random_customers(count=10):
    """
    Create random customers with random opportunity stages
    """
    customers = []
    statuses = list(CustomerStatus)
    opportunity_stages = list(OpportunityStage)

    for _ in range(count):
        customer = Customer(
            id=uuid4(),
            name=fake.company(),
            email=fake.company_email(),
            phone=fake.phone_number(),
            address=fake.address(),
            company=fake.company(),
            status=random.choice(statuses),
            source=fake.word(),
            notes=f"Random opportunity stage: {random.choice(opportunity_stages).value}"
        )
        customers.append(customer)
        # Add to Redis
        redis_manager.create(CUSTOMER_MODEL_TYPE, customer)
        print(f"Created customer: {customer.name} with ID: {customer.id}")

    return customers

def create_random_contacts(count=10):
    """
    Create random contacts
    """
    contacts = []

    for _ in range(count):
        contact = Contact(
            id=uuid4(),
            name=fake.name(),
            email=fake.email(),
            phone=fake.phone_number(),
            address=fake.address()
        )
        contacts.append(contact)
        # Add to Redis
        redis_manager.create(CONTACT_MODEL_TYPE, contact)
        print(f"Created contact: {contact.name} with ID: {contact.id}")

    return contacts

def create_random_opportunities(customers, count=15):
    """
    Create random opportunities for the given customers
    """
    opportunities = []
    stages = list(OpportunityStage)

    for _ in range(count):
        # Select a random customer
        customer = random.choice(customers)

        # Generate a random close date between now and 90 days in the future
        close_date = datetime.now() + timedelta(days=random.randint(1, 90))

        # Generate a random amount between 1000 and 100000
        amount = round(random.uniform(1000, 100000), 2)

        # Generate a random probability based on the stage
        stage = random.choice(stages)
        if stage == OpportunityStage.CLOSED_WON:
            probability = 100
        elif stage == OpportunityStage.CLOSED_LOST:
            probability = 0
        else:
            probability = random.randint(1, 99)

        opportunity = Opportunity(
            id=uuid4(),
            name=fake.catch_phrase(),
            customer_id=customer.id,
            amount=amount,
            stage=stage,
            expected_close_date=close_date,
            probability=probability,
            description=fake.paragraph()
        )

        opportunities.append(opportunity)
        # Add to Redis
        redis_manager.create(OPPORTUNITY_MODEL_TYPE, opportunity)
        print(f"Created opportunity: {opportunity.name} with ID: {opportunity.id} for customer: {customer.name}")

    return opportunities

def main():
    """
    Main function to populate Redis with random customers, contacts, and opportunities
    """
    print("Populating Redis with random customers, contacts, and opportunities...")

    try:
        # Test Redis connection
        redis_manager.redis_client.ping()

        # Create random customers with random opportunity stages
        customers = create_random_customers(10)
        print(f"Created {len(customers)} customers")

        # Create random contacts
        contacts = create_random_contacts(10)
        print(f"Created {len(contacts)} contacts")

        # Create random opportunities for the customers
        opportunities = create_random_opportunities(customers, 15)
        print(f"Created {len(opportunities)} opportunities")

        print("Done!")
    except redis.exceptions.ConnectionError:
        print("Error: Could not connect to Redis server.")
        print("Please make sure Redis is running at localhost:6379 or update the connection settings in the script.")
        print("You can start Redis with: docker run -d -p 6379:6379 redis")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
