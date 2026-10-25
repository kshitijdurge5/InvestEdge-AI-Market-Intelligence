from datetime import datetime,timedelta,timezone
import hashlib,secrets
from fastapi import APIRouter,HTTPException
from pydantic import BaseModel,EmailStr
router=APIRouter(prefix="/auth",tags=["authentication"]); USERS={}; OTPS={}
class SignupRequest(BaseModel): name:str; email:EmailStr; phone:str; password:str
class LoginRequest(BaseModel): identifier:str; password:str
class OTPRequest(BaseModel): identifier:str
class VerifyOTPRequest(BaseModel): identifier:str; otp:str
def h(x): return hashlib.sha256(x.encode()).hexdigest()
def find(x): return USERS.get(x.strip().lower())
@router.post("/signup")
def signup(p:SignupRequest):
 if len(p.password)<8: raise HTTPException(400,"Password must contain at least 8 characters.")
 e=p.email.lower().strip(); ph=p.phone.strip()
 if e in USERS or ph.lower() in USERS: raise HTTPException(409,"Account already exists.")
 u={"name":p.name.strip(),"email":e,"phone":ph,"password_hash":h(p.password)}; USERS[e]=u; USERS[ph.lower()]=u
 return {"message":"Account created. Please verify with OTP.","user":{"name":u["name"],"email":e,"phone":ph}}
@router.post("/login")
def login(p:LoginRequest):
 u=find(p.identifier)
 if not u or h(p.password)!=u["password_hash"]: raise HTTPException(401,"Invalid email/phone or password.")
 return {"message":"Login successful.","user":{"name":u["name"],"email":u["email"],"phone":u["phone"]}}
@router.post("/send-otp")
def send(p:OTPRequest):
 u=find(p.identifier)
 if not u: raise HTTPException(404,"No account found for this email/phone.")
 code=f"{secrets.randbelow(1000000):06d}"; OTPS[p.identifier.strip().lower()]=(code,datetime.now(timezone.utc)+timedelta(minutes=5)); print(f"\n[MARKETPILOT DEV OTP] {p.identifier}: {code}\n")
 return {"message":"OTP generated. Check the FastAPI terminal in development mode."}
@router.post("/verify-otp")
def verify(p:VerifyOTPRequest):
 k=p.identifier.strip().lower(); item=OTPS.get(k)
 if not item: raise HTTPException(400,"No OTP requested.")
 code,exp=item
 if datetime.now(timezone.utc)>exp: OTPS.pop(k,None); raise HTTPException(400,"OTP expired.")
 if p.otp.strip()!=code: raise HTTPException(400,"Incorrect OTP.")
 u=find(p.identifier); OTPS.pop(k,None)
 return {"message":"OTP verified successfully.","user":{"name":u["name"],"email":u["email"],"phone":u["phone"]}}
@router.post("/logout")
def logout(): return {"message":"Logged out successfully."}
