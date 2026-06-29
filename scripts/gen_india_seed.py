"""Generate a curated India-specific seed corpus for the text classifier.

The public corpora (UCI SMS, Enron) are Western and contain *no* Indian
transactional/delivery messages — so the model treated legit Zomato/Blinkit/bank
notices as out-of-distribution and false-flagged them. This module hand-authors a
diverse, realistic set of Indian SCAM and legitimate (HAM) messages to teach the
model the right local distribution.

Writes data/curated/india_seed.csv (committed). Re-run after editing the lists.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

OUT = Path("data/curated/india_seed.csv")

# ----------------------------- SCAM (label = 1) -----------------------------
SCAM = [
    # KYC / account block
    "Dear customer your SBI account will be blocked today. Complete KYC immediately at sbi-kyc-verify.in to avoid suspension.",
    "Your PAN card not updated with Aadhaar. Account suspended. Update now: http://incometax-verify.xyz/update",
    "ICICI Bank: Your net banking is deactivated. Re-activate within 24 hours by submitting details here: icici-secure.in/login",
    "Your Paytm KYC has expired. Verify now or your wallet balance will be frozen. Click bit.ly/paytm-kyc",
    "URGENT: Your bank account will be deactivated due to incomplete KYC. Call 9876543210 immediately.",
    "Aadhaar verification pending. Your SIM card will be deactivated in 2 hours. Update Aadhaar at uidai-update.in",
    # Telecom / electricity disconnection
    "Dear customer your electricity will be disconnected tonight 9:30 pm as your bill not updated. Call 8123456789 immediately - BSES",
    "Your Airtel mobile number will be disconnected today. Complete e-KYC verification urgently to continue services.",
    "Power supply will be cut today due to pending bill of Rs 1240. Pay now to avoid disconnection: payelectricity.in",
    # Lottery / prize / KBC
    "Congratulations! Your number won Rs 25,00,000 in KBC lucky draw. To claim send your bank details on WhatsApp 7000012345.",
    "You have won a brand new iPhone 15 in Amazon Big Billion lucky draw! Claim your prize: amaz0n-rewards.xyz",
    "CONGRATULATIONS! You are selected for Rs 10 lakh government scheme. Pay Rs 4999 processing fee to receive funds.",
    "Your mobile number has won 5,00,000 in Flipkart anniversary offer. Share OTP to claim your reward now.",
    # Loan offers
    "Get instant personal loan up to 10 lakh approved in 5 minutes, no documents! Apply now: quickloan-approve.in",
    "Pre-approved loan of Rs 2,00,000 for you! Just pay Rs 1500 file charges to release the amount today.",
    # Job / work from home
    "Work from home and earn Rs 5000 daily! Just like YouTube videos. Pay Rs 500 registration. WhatsApp 9123456780.",
    "Part time job offer: earn 2000-8000 per day from home. No experience needed. Join on Telegram now.",
    "We are hiring! Amazon data entry job, salary 35000/month. Pay Rs 999 for ID card to start immediately.",
    # Investment / crypto / stock
    "Double your money in 15 days with our crypto trading bot! Guaranteed 100% returns. Limited slots, invest now.",
    "Join our VIP stock tips group and earn guaranteed 30% profit daily. Free entry today only, message admin.",
    "Invest Rs 10000 and get Rs 50000 in one month, 100% safe government bond scheme. Hurry limited offer.",
    # Courier / customs / parcel
    "Your FedEx parcel is held at customs. Pay Rs 250 clearance fee to release: fedex-clearance.xyz/pay",
    "India Post: Your package could not be delivered due to incomplete address. Update here: indiapost-redeliver.in",
    "Your parcel from DHL is pending. Customs duty Rs 350 unpaid. Pay now to avoid return: dhl-india-customs.top",
    "Dear customer, your delivery is on hold. Confirm your address and pay Rs 99 redelivery charge: track-parcel.link",
    # UPI / refund / cashback
    "You have a refund of Rs 1999 pending. Accept the request on your UPI app to receive the amount immediately.",
    "PhonePe cashback of Rs 500! Accept the collect request to credit your account now.",
    "Your payment failed but amount debited. Accept this UPI request to get your refund of Rs 2499.",
    "Scan this QR code to receive your prize money of Rs 5000 instantly in your bank account.",
    # Digital arrest / police / threat
    "This is Mumbai Cyber Police. A case is registered against your Aadhaar for money laundering. Call immediately or face arrest.",
    "Your phone number is linked to illegal activity. You are under digital arrest. Do not disconnect, pay bail to settle.",
    "We have your private videos. Pay Rs 50000 within 24 hours or we will share them with all your contacts.",
    "FedEx: Illegal items found in your parcel sent to your name. Police complaint filed. Call to verify your innocence.",
    # Card / reward points
    "Your HDFC credit card reward points worth Rs 8400 expiring today. Redeem now: hdfc-rewards.in/redeem",
    "Your SBI card will be charged Rs 9999 for membership. To cancel call 8000011223 and share OTP for verification.",
    "Your debit card is blocked due to suspicious activity. Verify card number and CVV here to unblock: card-unblock.in",
    # Fake delivery / order
    "Your order is out for delivery but address incomplete. Verify and pay Re 1 to confirm: delivery-confirm.xyz",
    "Amazon: Your order is on hold. Update your payment details to avoid cancellation: amazon-update-pay.in",
    # Bank refund / verify
    "Income Tax Refund of Rs 15,490 approved. Verify your account number and IFSC to receive: itr-refund.in",
    "Your salary account requires re-verification. Click and login to keep your account active: bank-reverify.top",
    "RBI alert: your account flagged. Submit Aadhaar and PAN immediately to prevent freezing of funds.",
    # SIM swap / OTP forwarding
    "Your SIM will be upgraded to 5G. Forward the OTP you receive to 9000011122 to complete the upgrade.",
    "To activate 5G on your number, share the 6-digit verification code sent to your phone with our executive.",
    # Fake customer care
    "Paytm customer care: your account has an issue. Call 8001234567 and follow steps to fix, keep your phone ready.",
    "PhonePe helpline: your transaction is stuck. Download AnyDesk and share the code so we can refund you.",
    "Facing problem with your order? Call Amazon helpline 7012345678 and share OTP for refund verification.",
    # Task / rating jobs
    "Hello! Earn Rs 50 per task by liking YouTube videos. Send screenshot to receive payment. Join: t.me/easytask",
    "Flipkart work from home: rate hotels and earn 3000 daily. Send hi on WhatsApp 8800011223 to begin.",
    "Your application is selected for online typing job, Rs 25000/month. Pay refundable deposit Rs 2000 to confirm.",
    # OLX / army / marketplace
    "I am an Army officer posted in Jammu, I want to buy your sofa. I will pay via Army UPI, accept the request first.",
    "Sir I am interested in your bike on OLX. I am in military, can't come, paying advance now, scan this QR to receive.",
    # Romance / matrimony
    "Hi dear, I am stuck at airport customs and need Rs 30000 to clear my gift parcel for you. Please send via UPI.",
    # Charity / scheme
    "PM Kisan Yojana: Rs 6000 approved for you. Submit your bank details and Aadhaar OTP to receive the installment.",
    "You are eligible for free LPG connection under Ujjwala scheme. Pay Rs 599 registration to claim immediately.",
    # WhatsApp / verification
    "Your WhatsApp will be deactivated. Verify your number by sending us the 6 digit code you just received.",
    "You have been added as admin of a group. Confirm by sharing the verification code sent to your WhatsApp.",
    # Insurance / tax
    "Your LIC policy will lapse today. Pay pending premium Rs 4500 now at lic-payonline.xyz to keep it active.",
    "GST notice: penalty pending against your firm. Pay within 24 hours to avoid legal action: gst-penalty.in",
    # Crypto / trading
    "Claim your free 0.5 BTC airdrop! Connect your wallet here to receive: crypto-airdrop-india.top",
    "Our Telegram trading group gives 95% accurate signals. Deposit Rs 5000 and withdraw Rs 20000 today.",
    # Free recharge / reward
    "Jio is giving free 3 months recharge on 25th anniversary! Claim now: jio-anniversary-offer.in",
    "Your number won free Rs 599 recharge from Airtel. Click to claim before it expires: airtel-reward.link",
    # Credit card
    "Your credit card limit can be increased to 5 lakh instantly. Share card number, expiry and CVV to upgrade.",
    "Reward points worth Rs 12000 will expire today. Login here to redeem: cardpoints-redeem.xyz",
    # Account debit threat
    "Rs 4999 will be auto-debited for premium membership renewal. To cancel, call 8009998887 and verify OTP.",
    # Bank verify variants
    "Dear user, your YONO SBI account is temporarily locked. Unlock now by verifying details: yono-unlock.in",
    "Kotak Bank: unusual login detected. Confirm it's you by entering your card and net banking password here.",
]

# ------------------------- LEGITIMATE / HAM (label = 0) -------------------------
HAM = [
    # Bank OTP / alerts (with "do not share")
    "123456 is your OTP for transaction of Rs 2,500 at Amazon. Do not share it with anyone. - HDFC Bank",
    "Your OTP is 884521. Valid for 10 minutes. Never share your OTP with anyone. - ICICI Bank",
    "Rs 5,000.00 credited to your A/c XX1234 on 12-06 by UPI. Avl Bal Rs 18,450.00 - SBI",
    "Rs 1,240.00 debited from A/c XX5678 on 14-06 for electricity bill. Avl Bal Rs 9,210.00 - Axis Bank",
    "Your account XX9012 has been credited with salary Rs 65,000 on 30-06. - Kotak Bank",
    "Dear customer, Rs 239.00 paid to Zomato via UPI from A/c XX3456. Not you? Call 18001234.",
    "OTP for your SBI YONO login is 552134. Do not disclose to anyone including bank staff.",
    # Food delivery (Zomato / Swiggy / Blinkit)
    "Your Zomato order from Domino's Pizza has been confirmed and will arrive in 32 mins.",
    "Yum! Your Swiggy order is on the way. Rahul is arriving in 8 minutes with your food.",
    "Your Blinkit order has been placed successfully. Delivery in 12 minutes. Track in the app.",
    "Your Swiggy Instamart order of 9 items is packed and out for delivery.",
    "Order delivered! Hope you enjoyed your meal from Behrouz Biryani. Rate your experience on Zomato.",
    "Your Blinkit delivery partner is at your doorstep. Please collect your order.",
    # E-commerce orders
    "Your Amazon order of 'boAt earphones' has been shipped and will arrive by Friday. Track in Orders.",
    "Flipkart: Your order for Nike shoes is out for delivery today. Keep Rs 0 ready (Prepaid).",
    "Your Myntra order has been delivered. Loved it? Rate the product in the app.",
    "Order confirmed! Your Amazon package will be delivered tomorrow between 9 AM and 1 PM.",
    # Bills / recharge / utilities
    "Reminder: your Airtel postpaid bill of Rs 599 is due on 18-06. Pay via the Airtel Thanks app.",
    "Your Jio recharge of Rs 299 is successful. Validity 28 days, 2GB/day. Enjoy!",
    "Your electricity bill of Rs 1,420 for June is generated. Due date 25-06. Pay on the BESCOM portal.",
    "Your ACT Fibernet broadband bill of Rs 1,180 is due. Pay now to avoid service interruption.",
    "Your DTH recharge of Rs 350 is successful. Your Tata Play services are active.",
    # Travel / cab / train / flight
    "Your Ola ride is confirmed. Driver Suresh (KA01AB1234) will arrive in 4 minutes.",
    "Uber: Arriving now. Your driver is at the pickup point in a white Swift.",
    "PNR 2745019876 confirmed. Train 12627 Karnataka Express, coach B4, seat 32. Happy journey! - IRCTC",
    "Web check-in is open for your IndiGo flight 6E-234 BLR-DEL on 20-06. Select your seat in the app.",
    "Your redBus ticket from Bangalore to Chennai is booked. Boarding at 10:30 PM, seat L7.",
    # Appointments / services / personal
    "Your appointment with Dr. Mehta is confirmed for Monday 11:00 AM at Apollo Clinic. Reply RESCHEDULE to change.",
    "Your Urban Company service is booked for tomorrow 3 PM. Our professional will call before arriving.",
    "Hey, are we still meeting for coffee tomorrow at 5?",
    "Don't forget mom's birthday is on Sunday. Let's plan a surprise!",
    "The team standup is moved to 10:30 AM. Please update your calendar.",
    "Congrats on the new job! Let's celebrate this weekend.",
    "Your booking at The Leela for 2 guests on 22-06 at 8 PM is confirmed. We look forward to hosting you.",
    "Your movie tickets for Inox, 7:15 PM show, seats H5 and H6 are confirmed. Enjoy!",
    # Legit account/service notices (no action-via-link)
    "Welcome to Google! Your new account is ready. Manage your settings anytime in your account.",
    "Your monthly account statement for June is now available in the HDFC Bank app.",
    "Thank you for your payment of Rs 999. Your Netflix subscription is active until 14 July.",
    "Your Amazon Prime membership has been renewed. Enjoy free fast delivery and Prime Video.",
    "Your LPG cylinder booking is confirmed. Delivery expected within 2 working days. - Indane",
    # More OTP / auth (legit)
    "G-884213 is your Google verification code. Don't share it with anyone.",
    "554120 is your WhatsApp code. For your security, do not share this code.",
    "Your Uber verification code is 4421. Do not share this with anyone.",
    "Use OTP 730912 to log in to Paytm. Do not share this OTP. It is valid for 5 minutes.",
    "Dear customer, 218764 is the OTP to confirm your booking. Please do not share it. - MakeMyTrip",
    # Bank transactions (legit)
    "Transaction successful. Rs 1,250 paid to Swiggy via UPI from A/c XX4567. - Axis Bank",
    "Your EMI of Rs 8,499 for Bajaj Finserv loan has been auto-debited from A/c XX7788.",
    "Rs 2,000 has been transferred to Priya Sharma successfully via UPI. UPI Ref 412233445566.",
    "Your credit card bill of Rs 12,340 is due on 28-06. Pay via the bank app to avoid late fee.",
    "Cashback of Rs 25 received in your Paytm wallet for your recent transaction. Happy saving!",
    "Your account statement for Q1 is ready to download in net banking.",
    # Subscriptions / renewals (legit)
    "Your Disney+ Hotstar subscription has been renewed. Enjoy unlimited entertainment.",
    "Payment of Rs 119 received. Your Spotify Premium is active. Thanks for being a subscriber.",
    "Your annual car insurance is due for renewal on 05-07. Renew on the official portal to stay covered.",
    # Govt / institutional (legit)
    "Your CoWIN vaccination certificate is ready. Download it from the official portal.",
    "Dear citizen, your new PAN card has been dispatched and will be delivered shortly via Speed Post.",
    "LPG subsidy of Rs 291 has been credited to your bank account. - Bharat Gas",
    "Your passport application has been received. Track the status using your file number on the portal.",
    "Your driving licence renewal appointment is confirmed for 24-06 at RTO Indiranagar.",
    # Education / work (legit)
    "Your semester results are now available on the university portal. Best of luck!",
    "Reminder: your college fee installment is due on 30-06. Pay through the student portal.",
    "Your PF withdrawal claim has been processed and the amount will be credited in 3-5 working days. - EPFO",
    "Your salary slip for June is available on the HR portal. - Infosys",
    # Travel / delivery (legit)
    "Your IRCTC ticket is confirmed. PNR 8456231907. Carry a valid ID proof while travelling.",
    "Your Ola Auto has arrived. OTP 4412. Share it with the driver to start the ride.",
    "Your Amazon package was delivered. Returns are open for 7 days in the Orders section.",
    "Your gas cylinder will be delivered today between 10 AM and 2 PM. Keep Rs 1,103 ready. - HP Gas",
    "Your domino's order is being prepared and will be delivered in 30 minutes.",
    # Reminders / personal (legit)
    "Reminder: your dentist appointment is tomorrow at 4 PM. Reply Y to confirm.",
    "Gym membership expiring in 3 days. Renew at the front desk to continue your fitness journey.",
    "Hey, sending you the photos from yesterday's trip. Such a fun day!",
    "Please review the attached document before our meeting at 2 PM.",
    "Your library book is due on Friday. Return or renew to avoid a fine.",
    "Thanks for shopping with us! Your DMart bill is attached. Visit again.",
    "Your electricity bill payment of Rs 1,420 was successful. Thank you. - BESCOM",
]


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rows = [{"text": t, "label": 1, "source": "india_seed"} for t in SCAM]
    rows += [{"text": t, "label": 0, "source": "india_seed"} for t in HAM]
    df = pd.DataFrame(rows).drop_duplicates(subset="text")
    df.to_csv(OUT, index=False)
    print(f"Wrote {OUT}: {len(df)} rows ({int(df.label.sum())} scam / {int((df.label == 0).sum())} ham)")


if __name__ == "__main__":
    main()
