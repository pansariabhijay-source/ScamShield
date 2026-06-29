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
    # More bank / account
    "PNB customer: your account is temporarily suspended due to suspicious activity. Verify at pnb-secure-verify.in to restore access.",
    "Bank of Baroda: your debit card has been deactivated. Reactivate by confirming your 16-digit card number and OTP now.",
    "Canara Bank: your KYC is incomplete. Your account will be frozen in 24 hours. Update at canara-kyc.in immediately.",
    "IndusInd Bank: a login from a new device was detected. If this wasn't you, verify here: indusind-alert.top",
    "Union Bank: your internet banking password has expired. Reset now to avoid lock: unionbank-reset.in",
    "Dear customer, your account was wrongly credited with Rs 9,500. Return the amount via this UPI immediately to avoid legal action.",
    "Your account shows a pending charge of Rs 7,999. If unauthorized, call 8009990001 and share OTP to reverse it.",
    "Your bank account is marked dormant. Reactivate within 24 hours by verifying details or it will be closed: bank-reactivate.top",
    "I am calling from your bank head office. Your account has a security issue. Share the OTP I just sent to fix it.",
    "Your Paytm wallet will be blocked as per RBI guidelines. Complete KYC now: paytm-rbi-kyc.top",
    "Your SBI net banking will be locked. Verify your username and password at onlinesbi-verify.top immediately.",
    # Refunds / e-commerce
    "Amazon: your refund of Rs 1,299 failed. Update your bank details to receive it: amazon-refund-claim.in",
    "Flipkart: your order was cancelled. Claim your refund of Rs 2,450 before it expires: flipkart-refund.xyz",
    "Your IRCTC ticket refund of Rs 1,820 is on hold. Verify your account to receive: irctc-refund.top",
    "Your Swiggy order was cancelled due to a payment issue. Accept the refund request of Rs 449 on your UPI app.",
    "Your Nykaa order won a free gift hamper! Pay Rs 199 to claim and confirm your address.",
    # Utilities / electricity
    "Dear consumer, your electricity will be disconnected tonight for non-payment. Contact 7011223344 now. - MSEB",
    "TNEB: your power bill is overdue. Pay Rs 1,560 now to avoid disconnection within 2 hours: tneb-billpay.in",
    "Adani Electricity: your meter shows a pending amount. Update your details to avoid penalty: adani-power.top",
    "Your electricity bill of Rs 8 is pending, power will be cut in 1 hour. Call 9000088000 to pay. - power dept",
    "Your domestic gas subsidy is on hold. Update your Aadhaar-linked bank account now: gas-subsidy.in",
    # Loans
    "Congratulations! Your loan of Rs 3,00,000 is sanctioned. Pay Rs 2,100 processing fee to transfer the amount.",
    "Instant loan approved, no CIBIL check! Download our app and pay Rs 999 insurance to release funds.",
    "Final notice: your loan from XYZ app is overdue. We will inform your contacts. Pay Rs 4,500 now to settle.",
    "Get a personal loan of 5 lakh at 0% interest! Limited govt offer. Apply and pay Rs 1,500 file charge.",
    # Lottery / prize
    "You won Rs 10,00,000 in the Reliance Jio lucky draw! To claim, send your Aadhaar and bank details on WhatsApp.",
    "Tata Group 75th anniversary: you won a Tata Nexon! Pay Rs 6,500 registration to receive your car.",
    "Your WhatsApp number is selected in the Coca-Cola lucky draw for Rs 25 lakh. Contact our agent to claim.",
    "Dear winner, your email won 5,00,000 GBP in the UK National Lottery. Send your details to claim.",
    "You have an inheritance of $2.5 million from a deceased relative. Send your bank details to transfer the funds.",
    "Croma lucky customer! You won a Samsung TV. Pay Rs 2,500 delivery charges to claim your prize.",
    "Win an iPhone 15 Pro! You are the lucky 1000th visitor. Claim your prize: iphone-winner.xyz",
    # Jobs
    "Naukri: your profile is shortlisted for a Rs 45,000/month remote job. Pay Rs 1,500 for document verification.",
    "Earn Rs 2000-5000 daily by completing simple captcha typing tasks. Limited seats, pay Rs 700 to register.",
    "Amazon hiring work from home! Just review products and earn. Join our Telegram group and deposit Rs 1,000 to start.",
    "Part-time reselling job: earn Rs 1500 per order. Join the WhatsApp group and pay Rs 500 joining fee.",
    "You are selected as a brand ambassador! Earn Rs 50,000/month. Pay Rs 2,000 onboarding kit fee to start.",
    "We are hiring movie reviewers! Watch trailers, earn Rs 150 each. Pay Rs 500 membership to join.",
    # Investment / crypto
    "Guaranteed IPO allotment! Invest Rs 50,000 in our pre-IPO offer and get 3x returns at listing.",
    "Join our Telegram group for daily stock tips, 100% profit guaranteed. Free entry today, deposit to start.",
    "Binance USDT giveaway! Send 100 USDT to this wallet and receive 200 USDT back instantly.",
    "Our crypto mining plan gives 8% daily returns. Invest now and withdraw anytime: cryptomine-india.top",
    "Your investment of Rs 25,000 has grown to Rs 1,80,000! To withdraw, pay 10% tax of Rs 18,000 first.",
    "Your trading account profit of Rs 2,00,000 is ready. Pay processing charge of Rs 12,000 to withdraw.",
    "RBI launched a new digital rupee reward. Register and deposit Rs 1,000 to receive Rs 5,000 bonus.",
    "Hi, I think we matched earlier. I make great returns on a crypto platform, let me guide you to invest together.",
    # Courier / parcel
    "Blue Dart: your parcel is on hold due to incomplete address. Update and pay Rs 45 redelivery: bluedart-track.in",
    "Delhivery: your package delivery failed. Reschedule and pay Rs 30 handling fee: delhivery-reschedule.xyz",
    "DTDC: customs duty of Rs 499 is pending on your international parcel. Pay now to release it.",
    "You have an unclaimed gift parcel from abroad worth Rs 80,000. Pay Rs 1,800 customs clearance to receive it.",
    "Ecom Express: your COD order needs address confirmation. Verify here to avoid return: ecom-confirm.top",
    "You missed a parcel delivery. Reschedule and pay Rs 25: indiapost-track.top",
    # UPI / QR
    "I accidentally sent Rs 5,000 to your number. Please return it via this UPI request, I am in urgent need.",
    "To receive your Rs 2,000 cashback, scan this QR code and enter your UPI PIN to confirm.",
    "PhonePe: you have a pending payment request of Rs 1. Approve it to keep your account active.",
    "Google Pay reward of Rs 800 is waiting. Accept the request in your app to credit it instantly.",
    "Your account is selected for a special cashback of Rs 5,000. Scan QR and approve to receive it.",
    "Your Zomato Gold membership has a refund of Rs 800. Accept the UPI request to receive it.",
    # Sextortion / threat
    "We recorded you through your webcam. Send Rs 40,000 in 12 hours or the video goes to your family and friends.",
    "I have access to your phone and gallery. Transfer Rs 25,000 now or I leak everything to your contacts.",
    "Your social media account has been hacked. We have your private chats. Pay to delete them or they go public.",
    # Digital arrest / police / threat
    "This is CBI. Your Aadhaar is used in a money laundering case. Join the video call now or a warrant will be issued.",
    "TRAI notice: your number will be suspended for illegal activity. Press 9 to talk to an officer immediately.",
    "ED notice: your bank accounts are under investigation. Cooperate by sharing details or face immediate arrest.",
    "Narcotics found in a parcel booked under your name and Aadhaar. Call the Customs officer now to clear your name.",
    "We are from the Cyber Crime Branch. Your SIM is linked to a fraud. Stay on call and verify your bank balance.",
    "Your vehicle has a pending traffic challan of Rs 1,000. Pay now to avoid court summons: echallan-pay.top",
    # Cards
    "Your SBI credit card will be charged Rs 4,999 annual fee tomorrow. To waive it, share card number and OTP.",
    "Your HDFC debit card is blocked. Unblock instantly by verifying card details here: hdfc-card-unblock.in",
    "Axis Bank: redeem your 15,000 expiring reward points worth Rs 7,500 now: axis-rewards.xyz",
    "Your credit card application is approved. Pay Rs 599 activation fee to get your card delivered.",
    "Your credit card limit can be increased to 5 lakh. Share card number, expiry and CVV to upgrade.",
    # KYC / Aadhaar / SIM
    "Your Aadhaar will be deactivated due to inactivity. Re-verify with OTP at uidai-reverify.in immediately.",
    "Your mobile SIM KYC is pending. Complete it within 24 hours or your number will be disconnected. Call 8001112223.",
    "Your PAN will be deactivated for not linking with Aadhaar. Link now and pay Rs 500 penalty: pan-link.in",
    "Your Aadhaar is linked to 5 SIM cards illegally. Call the TRAI helpline now or face legal action.",
    "URGENT from Airtel: your SIM Aadhaar verification failed. Re-verify now or lose your number: airtel-kyc.in",
    "Dear user, your KYC video verification is pending for your demat account. Complete now: demat-kyc.top",
    # Govt schemes
    "You are selected for a free laptop under the Digital India scheme. Pay Rs 1,200 shipping to receive it.",
    "PMAY housing subsidy of Rs 2.5 lakh approved for you. Submit bank and Aadhaar details to claim.",
    "National Scholarship: Rs 50,000 granted. Verify your account and OTP to receive the amount.",
    "Your ration card needs e-KYC. Complete it at ration-kyc.in or your card will be cancelled.",
    "Your electricity subsidy of Rs 2,000 is approved. Share bank account and OTP to receive it.",
    # Insurance / tax
    "Your LIC policy bonus of Rs 1,80,000 is ready for release. Pay GST of Rs 9,000 to receive the full amount.",
    "Income Tax: you have an outstanding demand of Rs 12,400. Pay immediately to avoid prosecution: itax-pay.top",
    "Your health insurance claim is approved. Confirm your bank account and OTP to receive Rs 45,000.",
    "TDS refund of Rs 8,900 is pending. Update your account details to receive it: tds-refund.in",
    "Dear taxpayer, your GST refund of Rs 22,000 is approved. Confirm bank details to receive: gst-refund.in",
    # WhatsApp / family / screen-share
    "Mom, I lost my phone, this is my new number. I urgently need Rs 15,000, please send to this UPI, I'll explain later.",
    "Hi, this is your manager. I'm in a meeting, quickly buy 5 Amazon gift cards of Rs 2000 each and send the codes.",
    "To resolve your complaint, please download the Quick Support app and share the 9-digit code with our executive.",
    "Your WhatsApp is being used on another device. Send us the verification code to secure your account.",
    "Hi dear, can you do me a favour? I can't pay online right now, please pay Rs 8,000 for me and I'll return it tomorrow.",
    # FASTag / misc
    "Your FASTag is blacklisted. Recharge and update KYC now to avoid double toll: fastag-kyc.top",
    "Your recharge of Rs 299 failed but amount was deducted. To get a refund, call 7009998881 and share UPI PIN.",
    "Get a verified blue tick on Instagram! Pay Rs 999 and share your login to activate verification.",
    "Your Google account will be deleted for a policy violation. Verify now to keep it active: google-verify.top",
    "Your UPI app needs an urgent update. Failure to update will block transactions. Click: upi-update.top",
    "Your child's school fee is pending. Pay urgently via this link to avoid removal from class: schoolfee-pay.top",
    "Your Flipkart Plus membership expired. Renew now and claim a Rs 1,000 bonus: flipkart-plus.xyz",
    "Your number won Rs 9 lakh in the BSNL lucky draw. Contact the agent on WhatsApp with bank details to claim.",
    "Your SIP has matured early with 200% returns. Pay maturity tax to withdraw Rs 4,50,000.",
    "I want to rent your flat posted online. I'm transferring 2 months advance now, accept the UPI request to confirm.",
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
    # More OTP / auth (legit)
    "Your Zerodha Kite login OTP is 472913. Do not share it with anyone.",
    "Use 619284 to verify your Groww account. Never share this OTP.",
    "BigBasket: 338271 is your OTP to confirm your order. Do not share.",
    "Your Amazon OTP is 902817. Do not share it with anyone, including Amazon staff.",
    "Rapido: your ride OTP is 4471. Share it with the captain to start your ride.",
    "Your CRED login OTP is 552310. Valid for 5 minutes. Do not share.",
    "PNB: 781234 is your OTP for a fund transfer of Rs 3,000. Do not disclose to anyone.",
    "Your Upstox verification code is 339102. Keep it confidential.",
    "Flipkart: OTP 220488 to confirm your delivery. Share with the delivery agent only.",
    "Your SBI YONO OTP is 410982. Do not share. Valid for 5 minutes.",
    # Bank transactions (legit)
    "Rs 1,500 debited from A/c XX2233 via UPI to Reliance Fresh. Avl Bal Rs 7,800. - PNB",
    "Rs 25,000 transferred via IMPS to your A/c XX4455. Ref 9988776655. - Canara Bank",
    "ATM withdrawal of Rs 5,000 from A/c XX6677 at Koramangala. Avl Bal Rs 12,300. - HDFC",
    "Rs 899 spent on your Axis credit card at Amazon. Avl limit Rs 48,000.",
    "NEFT of Rs 50,000 credited to your A/c XX8899 from ABC Pvt Ltd. - ICICI",
    "Rs 320 paid via UPI to an auto driver. UPI Ref 778899001122. - SBI",
    "Your A/c XX1122 is debited Rs 12,499 for SIP in Axis Bluechip Fund.",
    "Your salary of Rs 78,000 has been credited to your account. - Wipro Payroll",
    "Cashback of Rs 50 credited to your CRED account for your bill payment.",
    "Rs 1,250 refunded to your original payment method for the cancelled Amazon order.",
    # Bills / utilities (legit)
    "Your BSNL broadband bill of Rs 799 for June is ready. Pay by 20th to avoid late charges.",
    "Recharge successful! Rs 239 added to your Vi number. Validity 28 days. Enjoy.",
    "Your Tata Power electricity bill of Rs 2,140 is due on 22-06. Pay via the official app.",
    "Your FASTag is recharged with Rs 500. Available balance Rs 720. - Paytm FASTag",
    "Your water bill of Rs 410 has been generated. Due date 28-06. - BWSSB",
    "Your mobile bill payment of Rs 599 is successful. Thank you for using Airtel.",
    "Reminder: your broadband bill of Rs 999 is due tomorrow. - JioFiber",
    "Your PhonePe transaction of Rs 600 to BESCOM was successful. Thank you.",
    # E-commerce orders (legit)
    "Your Ajio order has been shipped and will be delivered by Saturday. Track in the app.",
    "Nykaa: your order is out for delivery today. Get ready to glow!",
    "Meesho: your order has been confirmed and will arrive in 5-7 days.",
    "Your JioMart order is packed and will be delivered tomorrow morning.",
    "Croma: your TV will be delivered and installed on 24-06 between 10 AM and 6 PM.",
    "Your BigBasket order of 14 items is out for delivery. Arriving in 45 mins.",
    "Tata CLiQ: your order has been delivered. Rate your experience in the app.",
    "Your Amazon order of 'Atomic Habits' has shipped. Arriving Wednesday.",
    "Your Myntra return has been picked up. Refund of Rs 1,499 will reflect in 3-5 days.",
    "Your Decathlon order is ready for pickup at the Whitefield store.",
    "Your Nykaa order has been delivered. Enjoy your products!",
    # Food delivery (legit)
    "Your Swiggy order from Faasos is being prepared. Estimated delivery 25 mins.",
    "Zomato: your order has been picked up and is 2 stops away.",
    "Your EatSure order is on the way. Track your rider live in the app.",
    "Your Swiggy Instamart order is delivered. Hope you got everything you needed!",
    # Travel (legit)
    "Your IndiGo flight 6E-512 BLR-BOM is on time. Boarding at 6:10 PM, Gate 24.",
    "Your Ola cab is arriving. Driver Ramesh in a grey Dzire, KA05CD6789. OTP 3312.",
    "PNR 4561237890 RAC. Train 12658 Chennai Mail. We'll notify you on confirmation. - IRCTC",
    "Your redBus boarding point is MG Road at 9:45 PM. Carry a valid ID. Happy journey!",
    "Your metro smart card is recharged with Rs 200. Balance Rs 260. - Namma Metro",
    "Your Uber trip receipt: Rs 245 for your ride to the airport. Thanks for riding with Uber.",
    "Your booking at OYO Townhouse for 2 nights is confirmed. Check-in 2 PM.",
    "Your flight web check-in is complete. Boarding pass sent to your email. - Vistara",
    "Your booking for the Bangalore-Mysore Volvo bus is confirmed. Seat 21A. - KSRTC",
    # Subscriptions / services (legit)
    "Your SonyLIV subscription is active until 30 July. Enjoy unlimited streaming.",
    "Payment of Rs 149 received. Your YouTube Premium is renewed. Thank you.",
    "Your Audible membership has been renewed. 1 credit added to your account.",
    "Your Urban Company salon appointment is confirmed for today 5 PM. Our professional will arrive on time.",
    "Your booking at Cult.fit for tomorrow's 7 AM session is confirmed.",
    # Govt / institutional (legit)
    "Your Income Tax Return for AY 2024-25 has been successfully e-verified. - Income Tax Department",
    "Your EPF passbook is updated. Employer contribution of Rs 3,600 credited for June. - EPFO",
    "Your GSTR-3B for May has been filed successfully. ARN generated. - GSTN",
    "Your Aadhaar update request is successful. Updated details will reflect in 7 days. - UIDAI",
    "Your driving licence has been approved and dispatched. Track on the Parivahan portal.",
    "Your appointment token number is 27. Please wait for your turn. - Aadhaar Seva Kendra",
    "Your gas booking is confirmed. The cylinder will be delivered within 2 days. - Bharat Gas",
    # Education / health (legit)
    "Your child's exam timetable for the final term is now available on the school portal.",
    "Your admit card for the semester exam is ready. Download from the university portal.",
    "Your lab reports from Dr. Lal PathLabs are ready. View them in the app or collect from the centre.",
    "Your medicine order from PharmEasy has been shipped and will arrive tomorrow.",
    "Your dentist appointment at Clove Dental is confirmed for Saturday 11 AM.",
    "Your appointment at Apollo Diagnostics for a blood test is confirmed for 8 AM tomorrow.",
    # Finance (legit)
    "Your Zerodha contract note for today's trades is available. Download from Console.",
    "Your mutual fund SIP of Rs 5,000 in HDFC Flexi Cap is processed. Units allotted.",
    "Your credit card statement for June is generated. Total due Rs 8,200. Min due Rs 410. Due 28-06.",
    "Your car insurance premium of Rs 14,200 is paid. Policy active till 04-07-2025. - ICICI Lombard",
    "Your LIC premium of Rs 18,500 received. Thank you. Next due 04-12.",
    "Your Groww order to buy 10 shares of TCS is executed at Rs 3,820.",
    "Your monthly mutual fund statement is now available. - CAMS",
    # Personal / social / work (legit)
    "Hey, are you free this weekend? Was thinking we could go trekking.",
    "Happy birthday! Wishing you a fantastic year ahead. Let's catch up soon.",
    "Reminder: parent-teacher meeting tomorrow at 10 AM. Please be on time.",
    "The client call is rescheduled to 4 PM. I've sent a new calendar invite.",
    "Thanks for the help yesterday, really appreciate it!",
    "Can you share the presentation slides before EOD? Thanks.",
    "Dinner at 8 tonight? Let me know if that works for you.",
    "Your table for 4 at Barbeque Nation is confirmed for 7:30 PM today.",
    "Your BookMyShow tickets for the 9 PM show are booked. Seats J12, J13. Enjoy!",
    "Your gym membership has been renewed for one year. Happy training!",
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
