from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# In-memory database for users and their balances
db = {
    "Rumaisa": {"pin": "1234", "balance": 1000},
    "Areeba": {"pin": "5678", "balance": 500},
    "Aliza": {"pin": "9876", "balance": 2000},
}

class UserCredentials(BaseModel):
    name: str
    pin: str

class TransferRequest(BaseModel):
    sender_name: str
    recipient_name: str
    amount: float

@app.post("/authenticate")
async def authenticate(credentials: UserCredentials):
    user = db.get(credentials.name)
    if not user or user["pin"] != credentials.pin:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": f"Authentication successful for {credentials.name}."}

@app.post("/banktransfer")
async def bank_transfer(request: TransferRequest):
    sender = db.get(request.sender_name)
    recipient = db.get(request.recipient_name)

    if not sender:
        raise HTTPException(status_code=404, detail=f"Sender '{request.sender_name}' not found.")
    if not recipient:
        raise HTTPException(status_code=404, detail=f"Recipient '{request.recipient_name}' not found.")

    if sender["balance"] < request.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds.")

    # Perform the transfer
    sender["balance"] -= request.amount
    recipient["balance"] += request.amount

    return {
        "message": "Transfer successful.",
        "sender": request.sender_name,
        "recipient": request.recipient_name,
        "transferred_amount": request.amount,
        "new_sender_balance": sender["balance"],
    }

@app.get("/balance/{name}")
async def get_balance(name: str):
    user = db.get(name)
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{name}' not found.")
    return {"name": name, "balance": user["balance"]}