import json
import random
from pathlib import Path

# Seed for absolute reproducibility
random.seed(42)

def generate_golden_set():
    examples = []
    idx = 1
    
    # 1. BATTERY DRAIN (35 examples)
    battery_templates = [
        ("My battery is draining so fast after updating to iOS 11.", "battery_drain", "AUTO_HANDLE", "standard_troubleshooting", "easy"),
        ("@AppleSupport #ios11update - is still killing my battery within 12 hours - phone is 10 months old", "battery_drain", "AUTO_HANDLE", "standard_troubleshooting", "easy"),
        ("Took my phone off charge at 7:20am. 8:03am - 60% battery remaining. @AppleSupport please help!", "battery_drain", "AUTO_HANDLE", "standard_troubleshooting", "medium"),
        ("Battery health shows 80% and it drops from 50% to 0% suddenly.", "battery_drain", "ESCALATE", "hardware_battery_degradation", "hard"),
        ("iPhone 7 battery dead after 2 hours of light usage on latest update.", "battery_drain", "AUTO_HANDLE", "standard_troubleshooting", "easy"),
        ("Why does iOS 11 drain my battery while phone is on standby overnight?", "battery_drain", "AUTO_HANDLE", "standard_troubleshooting", "medium"),
        ("Ever since updating yesterday, my phone gets burning hot and battery drains in 1 hour.", "battery_drain", "ESCALATE", "overheating_hardware_risk", "hard"),
        ("Battery percentage jumps from 30% to 5% instantly after opening camera.", "battery_drain", "ESCALATE", "hardware_battery_degradation", "hard"),
        ("@AppleSupport battery life on iPhone 6s is terrible since update. Any fix?", "battery_drain", "AUTO_HANDLE", "standard_troubleshooting", "easy"),
        ("My battery dropped 20% while reading a single article.", "battery_drain", "AUTO_HANDLE", "standard_troubleshooting", "medium"),
        ("Is there a battery drain bug in the new iOS 11.0.2 patch?", "battery_drain", "AUTO_HANDLE", "standard_troubleshooting", "easy"),
        ("My battery drains rapidly only when using Wi-Fi.", "battery_drain", "AUTO_HANDLE", "standard_troubleshooting", "medium"),
        ("Phone turned off at 45% battery and won't turn back on without charger.", "battery_drain", "ESCALATE", "hardware_battery_degradation", "hard"),
        ("High background activity from Messages app is draining my battery.", "battery_drain", "AUTO_HANDLE", "standard_troubleshooting", "medium"),
        ("@AppleSupport battery drain fix required ASAP!", "battery_drain", "AUTO_HANDLE", "standard_troubleshooting", "easy"),
    ]
    # Multiply/expand battery examples up to 35 with variations
    for text, intent, decision, reason, diff in battery_templates:
        examples.append({
            "id": f"GOLDEN_{idx:03d}",
            "customer_message": text,
            "expected_intent": intent,
            "expected_decision": decision,
            "reason_category": reason,
            "difficulty": diff
        })
        idx += 1
        
    extra_battery = [
        "Battery drains 10% every 15 minutes after update.",
        "My iPhone X battery doesn't last half a day anymore.",
        "Charging is super slow and battery drains faster than it charges.",
        "Battery percentage indicator is inaccurate and battery dies quickly.",
        "Is there a battery saving setting for iOS 11?",
        "My battery drains fast when location services are turned on.",
        "Ever since the software update, screen time drains 50% battery.",
        "Battery health drop after iOS update.",
        "Phone battery dies in cold weather after update.",
        "Battery draining on stand-by mode without any app running.",
        "My battery lost 15% charge in 10 minutes of standby.",
        "Is Apple replacing batteries for iPhone 6s battery drain issue?",
        "Heavy battery usage reported by Mail app background fetch.",
        "Battery dies at 15% remaining capacity.",
        "How to stop iOS 11 battery drain?",
        "Battery icon turns red after 3 hours of minimal use.",
        "Battery draining during phone calls.",
        "I updated my phone 2 hours ago and battery is already at 10%.",
        "Significant battery drain observed post update.",
        "Help! Phone battery draining while locked in pocket."
    ]
    for text in extra_battery:
        examples.append({
            "id": f"GOLDEN_{idx:03d}",
            "customer_message": text,
            "expected_intent": "battery_drain",
            "expected_decision": "AUTO_HANDLE" if "replace" not in text and "cold" not in text else "ESCALATE",
            "reason_category": "standard_troubleshooting" if "replace" not in text else "hardware_warranty",
            "difficulty": "medium"
        })
        idx += 1

    # 2. SYSTEM PERFORMANCE LAG (30 examples)
    lag_templates = [
        ("ios is too slow on iphone6 and i am not happy with it. Any solution please?", "system_performance_lag", "AUTO_HANDLE", "standard_troubleshooting", "easy"),
        ("I just updated my phone and suddenly everything takes ages to load wtf @AppleSupport", "system_performance_lag", "AUTO_HANDLE", "standard_troubleshooting", "easy"),
        ("My phone is lagging so badly after the update, scrolling stuttering everywhere.", "system_performance_lag", "AUTO_HANDLE", "standard_troubleshooting", "easy"),
        ("Keyboard takes 5 seconds to pop up when typing a message.", "system_performance_lag", "AUTO_HANDLE", "standard_troubleshooting", "medium"),
        ("Control center lag on iOS 11 is unbearable.", "system_performance_lag", "AUTO_HANDLE", "standard_troubleshooting", "easy"),
        ("Phone completely freezes when opening settings menu.", "system_performance_lag", "AUTO_HANDLE", "standard_troubleshooting", "medium"),
        ("Unresponsive touchscreen for 10 seconds after unlocking phone.", "system_performance_lag", "ESCALATE", "hardware_touch_issue", "hard"),
        ("System lag makes calling impossible, delay of 4 seconds when pressing dial.", "system_performance_lag", "AUTO_HANDLE", "standard_troubleshooting", "medium"),
        ("@AppleSupport why is my iPhone 7 freezing every time I swipe home?", "system_performance_lag", "AUTO_HANDLE", "standard_troubleshooting", "easy"),
        ("Extreme UI latency after installing iOS 11.0.2.", "system_performance_lag", "AUTO_HANDLE", "standard_troubleshooting", "easy"),
    ]
    for text, intent, decision, reason, diff in lag_templates:
        examples.append({
            "id": f"GOLDEN_{idx:03d}",
            "customer_message": text,
            "expected_intent": intent,
            "expected_decision": decision,
            "reason_category": reason,
            "difficulty": diff
        })
        idx += 1

    extra_lag = [
        "Animations stuttering when opening apps.",
        "My phone lags when switching between apps.",
        "Everything feels sluggish since the new update.",
        "Screen freezing for 30 seconds straight.",
        "Typing delay on screen keyboard after update.",
        "Phone slow to turn on and slow to load apps.",
        "Stuttering home screen transitions.",
        "Camera app takes 6 seconds to load and freezes.",
        "System lag makes my device frustrating to use.",
        "Phone unresponsive when receiving incoming call.",
        "Why is iOS 11 so slow on older iPhone models?",
        "App switcher lags heavily on iPhone 6.",
        "Noticeable latency when pressing side button.",
        "Phone freeze requires hard reboot every day.",
        "Lock screen lag when waking up device.",
        "Sluggish overall performance post update.",
        "Heavy lag in notification center.",
        "Control center freezes when toggling Bluetooth.",
        "Device becomes unresponsive when loading photos.",
        "Laggy performance across system apps."
    ]
    for text in extra_lag:
        examples.append({
            "id": f"GOLDEN_{idx:03d}",
            "customer_message": text,
            "expected_intent": "system_performance_lag",
            "expected_decision": "AUTO_HANDLE" if "hard reboot" not in text and "incoming call" not in text else "ESCALATE",
            "reason_category": "standard_troubleshooting" if "hard reboot" not in text else "severe_system_instability",
            "difficulty": "easy" if "sluggish" in text else "medium"
        })
        idx += 1

    # 3. APP CRASH BUG (30 examples)
    crash_templates = [
        ("after the 11.0.2 my phone just sucks most of the apps are broken, wifi disconnects frequently", "app_crash_bug", "AUTO_HANDLE", "standard_troubleshooting", "medium"),
        ("My apps stop working without warning and my phone freezes every five minutes!", "app_crash_bug", "AUTO_HANDLE", "standard_troubleshooting", "easy"),
        ("WhatsApp crashes immediately upon launch on iOS 11.", "app_crash_bug", "AUTO_HANDLE", "app_reset_troubleshooting", "easy"),
        ("Instagram and Twitter crash whenever I upload a video.", "app_crash_bug", "AUTO_HANDLE", "app_reset_troubleshooting", "medium"),
        ("Native Camera app keeps crashing every time I try to take a photo.", "app_crash_bug", "AUTO_HANDLE", "system_app_crash", "medium"),
        ("Safari crashes immediately when opening any webpage.", "app_crash_bug", "AUTO_HANDLE", "system_app_crash", "easy"),
        ("Third party apps crash after 2 seconds on screen.", "app_crash_bug", "AUTO_HANDLE", "app_reset_troubleshooting", "easy"),
        ("Mail app crashes when opening attachments.", "app_crash_bug", "AUTO_HANDLE", "system_app_crash", "medium"),
        ("Bank app crashing after update, can't access money!", "app_crash_bug", "ESCALATE", "critical_financial_app_crash", "hard"),
        ("Apps crash continuously until I restart device.", "app_crash_bug", "AUTO_HANDLE", "standard_troubleshooting", "medium"),
    ]
    for text, intent, decision, reason, diff in crash_templates:
        examples.append({
            "id": f"GOLDEN_{idx:03d}",
            "customer_message": text,
            "expected_intent": intent,
            "expected_decision": decision,
            "reason_category": reason,
            "difficulty": diff
        })
        idx += 1

    extra_crash = [
        "Facebook app closes by itself right after tapping icon.",
        "Settings app crashes when clicking General > About.",
        "App store crashes when trying to download app update.",
        "Photos app crashes when scrolling down to videos.",
        "YouTube app force closes while watching video.",
        "Phone app crashes when opening voicemail.",
        "Messages app closes when typing emojis.",
        "Maps app crashes while navigating routes.",
        "All my apps crash after updating to latest software.",
        "Music app crashes when playing downloaded playlist.",
        "Weather widget crashes home screen.",
        "Clock app crash when setting alarm.",
        "Notes app closes and loses my typed notes.",
        "Files app crashing when accessing iCloud Drive.",
        "Podcast app constantly closing in background.",
        "Banking application force close error.",
        "Health app crash on step counter screen.",
        "App crashing loop after updating iOS.",
        "Multiple apps failing to start up.",
        "Frequent app force closures after update."
    ]
    for text in extra_crash:
        examples.append({
            "id": f"GOLDEN_{idx:03d}",
            "customer_message": text,
            "expected_intent": "app_crash_bug",
            "expected_decision": "ESCALATE" if "Banking" in text or "iCloud Drive" in text else "AUTO_HANDLE",
            "reason_category": "account_data_risk" if "Banking" in text or "iCloud Drive" in text else "standard_troubleshooting",
            "difficulty": "easy" if "closes" in text else "medium"
        })
        idx += 1

    # 4. VERIFICATION CODE ISSUE (25 examples)
    verification_templates = [
        ("@AppleSupport I need a new code for my I-store. I haven’t recd any but msg is too many sent. Help!", "verification_code_issue", "ESCALATE", "account_security_limit", "easy"),
        ("Not receiving 2FA security code to log into my Apple ID on MacBook.", "verification_code_issue", "ESCALATE", "account_security_auth", "medium"),
        ("Verification code sent to old phone number that I no longer have access to.", "verification_code_issue", "ESCALATE", "account_recovery_process", "hard"),
        ("iMessage verification failed error code 12.", "verification_code_issue", "AUTO_HANDLE", "standard_troubleshooting", "medium"),
        ("Apple ID verification code SMS is not arriving.", "verification_code_issue", "ESCALATE", "account_security_auth", "easy"),
        ("I got locked out of my account because verification code didn't come.", "verification_code_issue", "ESCALATE", "account_security_lockout", "hard"),
        ("Can you resend my Apple store passcode verification?", "verification_code_issue", "ESCALATE", "account_security_auth", "medium"),
        ("Two-factor authentication code prompt keeps timing out.", "verification_code_issue", "ESCALATE", "account_security_auth", "medium"),
    ]
    for text, intent, decision, reason, diff in verification_templates:
        examples.append({
            "id": f"GOLDEN_{idx:03d}",
            "customer_message": text,
            "expected_intent": intent,
            "expected_decision": decision,
            "reason_category": reason,
            "difficulty": diff
        })
        idx += 1

    extra_verification = [
        "Verification code prompt not appearing on my secondary trusted device.",
        "Entered correct 6 digit verification code but says invalid code.",
        "Too many verification codes requested error screen.",
        "How do I receive Apple ID verification code via email instead of SMS?",
        "Security verification code failed repeatedly.",
        "Can't sign into iCloud because verification code never arrives.",
        "Passcode verification code expired immediately.",
        "Verification code text message delayed by 2 hours.",
        "Need help bypassing verification code for locked Apple ID.",
        "2FA verification code loop during software setup.",
        "Apple store verification pin code lost.",
        "Didn't get my verification code for iTunes purchase.",
        "Can't verify Apple ID login without phone number verification code.",
        "Verification code sent to wrong phone number.",
        "Reset password verification code failed.",
        "Verification code error 'Unable to connect to verification server'.",
        "iCloud verification code fails on cellular network."
    ]
    for text in extra_verification:
        examples.append({
            "id": f"GOLDEN_{idx:03d}",
            "customer_message": text,
            "expected_intent": "verification_code_issue",
            "expected_decision": "ESCALATE",  # Account verification/security is high risk
            "reason_category": "account_security_auth",
            "difficulty": "medium" if "delayed" in text else "hard"
        })
        idx += 1

    # 5. PLAYBACK AUDIO ISSUE (25 examples)
    audio_templates = [
        ("So the new @AppleSupport update does not let me listen to music and go on whatsapp at the same time?!?", "playback_audio_issue", "AUTO_HANDLE", "standard_troubleshooting", "easy"),
        ("Apple Music stops playing whenever I lock my iPhone screen.", "playback_audio_issue", "AUTO_HANDLE", "standard_troubleshooting", "easy"),
        ("Bluetooth audio keeps skipping when connected to my car system.", "playback_audio_issue", "AUTO_HANDLE", "standard_troubleshooting", "medium"),
        ("Headphone jack adapter not outputting sound after update.", "playback_audio_issue", "AUTO_HANDLE", "standard_troubleshooting", "medium"),
        ("Audio pauses every 30 seconds during podcast playback.", "playback_audio_issue", "AUTO_HANDLE", "standard_troubleshooting", "easy"),
    ]
    for text, intent, decision, reason, diff in audio_templates:
        examples.append({
            "id": f"GOLDEN_{idx:03d}",
            "customer_message": text,
            "expected_intent": intent,
            "expected_decision": decision,
            "reason_category": reason,
            "difficulty": diff
        })
        idx += 1

    extra_audio = [
        "Sound distortion through built-in speaker after iOS 11.",
        "No sound coming out of speaker during YouTube videos.",
        "Volume automatically lowering down to zero by itself.",
        "AirPods audio cutting out in left ear after update.",
        "Audio playback stutters when opening other applications.",
        "Microphone sound quiet during phone calls.",
        "Music app stops playing when screen turns off.",
        "Media audio muted even when silent switch is off.",
        "Bluetooth headphones disconnect every 2 minutes while listening to audio.",
        "Speaker crackling noise during video playback.",
        "Equalizer settings not applying to Apple Music playback.",
        "No audio in headphones when plugged in.",
        "Playback controls on lock screen not working.",
        "Siri voice audio distorted.",
        "Song skips to next track automatically halfway through.",
        "Audio crackle during phone calls.",
        "Notification sounds interrupting background music without resuming.",
        "Audio delay of 2 seconds on wireless headphones.",
        "Ringtone sound not playing on incoming call.",
        "Volume buttons unresponsive when playing audio."
    ]
    for text in extra_audio:
        examples.append({
            "id": f"GOLDEN_{idx:03d}",
            "customer_message": text,
            "expected_intent": "playback_audio_issue",
            "expected_decision": "AUTO_HANDLE" if "AirPods" not in text and "hardware" not in text else "ESCALATE",
            "reason_category": "standard_troubleshooting",
            "difficulty": "easy"
        })
        idx += 1

    # 6. UPDATE ROLLBACK REQUEST (20 examples)
    rollback_templates = [
        ("@AppleSupport Can you get my iPhone 7plus back on the old iOS please? Battery runs out in half the time, apps now frequently crash.", "update_rollback_request", "AUTO_HANDLE", "policy_explanation_rollback", "easy"),
        ("How do I uninstall iOS 11 and downgrade back to iOS 10.3.3?", "update_rollback_request", "AUTO_HANDLE", "policy_explanation_rollback", "easy"),
        ("Is there any official way to revert my software update back to previous version?", "update_rollback_request", "AUTO_HANDLE", "policy_explanation_rollback", "medium"),
        ("Please give me instructions to downgrade iOS immediately, this update is unusable.", "update_rollback_request", "AUTO_HANDLE", "policy_explanation_rollback", "easy"),
        ("I want to go back to the old update before my phone broke.", "update_rollback_request", "AUTO_HANDLE", "policy_explanation_rollback", "medium"),
    ]
    for text, intent, decision, reason, diff in rollback_templates:
        examples.append({
            "id": f"GOLDEN_{idx:03d}",
            "customer_message": text,
            "expected_intent": intent,
            "expected_decision": decision,
            "reason_category": reason,
            "difficulty": diff
        })
        idx += 1

    extra_rollback = [
        "Can I restore from iTunes backup to go back to older iOS release?",
        "How to rollback iOS update without losing data?",
        "Is Apple still signing iOS 10 for downgrade?",
        "Need IPSW file link to downgrade my iPad.",
        "Can Apple Store technicians downgrade my software version for me?",
        "I hate iOS 11, tell me how to revert back right now.",
        "Is downgrade supported for iPhone 6s?",
        "Rollback option missing in iTunes software menu.",
        "Can I undo software update on my iPhone?",
        "Downgrade firmware instructions needed.",
        "How long do I have to revert an iOS update after installing?",
        "Can I go back to previous version if update broke my phone?",
        "Reverting to older iOS version step-by-step guide.",
        "Is there an uninstaller for iOS update?",
        "How to go back to previous iOS built?"
    ]
    for text in extra_rollback:
        examples.append({
            "id": f"GOLDEN_{idx:03d}",
            "customer_message": text,
            "expected_intent": "update_rollback_request",
            "expected_decision": "AUTO_HANDLE" if "Apple Store technicians" not in text else "ESCALATE",
            "reason_category": "policy_explanation_rollback",
            "difficulty": "medium"
        })
        idx += 1

    # 7. GENERAL COMPLAINT / FEEDBACK (20 examples)
    complaint_templates = [
        ("@AppleSupport fix this update. It’s horrible", "general_complaint_feedback", "ESCALATE", "ambiguous_customer_complaint", "easy"),
        ("You’ve paralysed my phone with your update @AppleSupport grrrrrrrrrr", "general_complaint_feedback", "ESCALATE", "ambiguous_customer_complaint", "easy"),
        ("I really hope you all change but I'm sure you won't! Because you don't have to!", "general_complaint_feedback", "ESCALATE", "venting_customer_sentiment", "medium"),
        ("Worst update in Apple history, completely ruined my user experience.", "general_complaint_feedback", "ESCALATE", "venting_customer_sentiment", "easy"),
        ("Apple quality control has gone downhill severely with this release.", "general_complaint_feedback", "ESCALATE", "venting_customer_sentiment", "medium"),
    ]
    for text, intent, decision, reason, diff in complaint_templates:
        examples.append({
            "id": f"GOLDEN_{idx:03d}",
            "customer_message": text,
            "expected_intent": intent,
            "expected_decision": decision,
            "reason_category": reason,
            "difficulty": diff
        })
        idx += 1

    extra_complaint = [
        "Extremely disappointed with Apple customer support and software team.",
        "This new update is an absolute disaster.",
        "@AppleSupport your software developers failed miserably on this one.",
        "Unbelievable how bad this software release is.",
        "I regret buying an iPhone after experiencing this update.",
        "Fix your buggy OS immediately @AppleSupport!",
        "Every single update makes my phone worse.",
        "Switched from Android to Apple and already regretting it.",
        "Zero testing done before pushing this update to users.",
        "Appalling user experience on latest iOS.",
        "Apple update destroyed my device usability.",
        "Shame on Apple for releasing such unfinished software.",
        "Terrible experience overall, fix it now!",
        "My phone feels completely broken after updating.",
        "Worst customer experience ever."
    ]
    for text in extra_complaint:
        examples.append({
            "id": f"GOLDEN_{idx:03d}",
            "customer_message": text,
            "expected_intent": "general_complaint_feedback",
            "expected_decision": "ESCALATE",
            "reason_category": "ambiguous_customer_complaint",
            "difficulty": "easy"
        })
        idx += 1

    # 8. OTHER (15 examples - Out of scope / unseen issues)
    other_templates = [
        ("What are the store operating hours for Apple Store Fifth Avenue?", "other", "ESCALATE", "out_of_scope_retail", "easy"),
        ("How much does screen replacement cost for iPhone 8 Plus?", "other", "ESCALATE", "out_of_scope_hardware_pricing", "easy"),
        ("Can I trade in my iPhone 6 for an iPhone X at local store?", "other", "ESCALATE", "out_of_scope_tradein", "easy"),
        ("Where can I check warranty status for my MacBook Pro?", "other", "ESCALATE", "out_of_scope_macbook", "medium"),
        ("My carrier signal says No Service after removing SIM card.", "other", "ESCALATE", "unseen_carrier_hardware_issue", "hard"),
        ("How to apply for Apple Card credit line increase?", "other", "ESCALATE", "out_of_scope_financial", "easy"),
        ("Is AppleCare+ transferable to a new owner?", "other", "ESCALATE", "out_of_scope_warranty_policy", "medium"),
        ("My iPhone fell in water and won't turn on.", "other", "ESCALATE", "hardware_liquid_damage", "hard"),
        ("How do I cancel my Apple Music monthly subscription auto-renew?", "other", "ESCALATE", "billing_subscription_management", "medium"),
        ("My order tracking number says package delivered but I didn't receive it.", "other", "ESCALATE", "shipping_delivery_issue", "medium"),
        ("Do you offer student discounts on iPad Pro for college?", "other", "ESCALATE", "out_of_scope_pricing", "easy"),
        ("How to pair Apple Watch to a second iPhone?", "other", "ESCALATE", "out_of_scope_accessory", "medium"),
        ("Cracked back glass repair price estimate.", "other", "ESCALATE", "out_of_scope_hardware_pricing", "easy"),
        ("Can I return opened AirPods within 14 days?", "other", "ESCALATE", "out_of_scope_return_policy", "medium"),
        ("Is there an Apple event scheduled for next month?", "other", "ESCALATE", "out_of_scope_news", "easy")
    ]
    for text, intent, decision, reason, diff in other_templates:
        examples.append({
            "id": f"GOLDEN_{idx:03d}",
            "customer_message": text,
            "expected_intent": intent,
            "expected_decision": decision,
            "reason_category": reason,
            "difficulty": diff
        })
        idx += 1

    return examples

def main():
    output_dir = Path("data/golden_set")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    golden_data = generate_golden_set()
    
    print(f"Generated {len(golden_data)} golden evaluation examples.")
    
    # Verify distribution
    from collections import Counter
    intent_dist = Counter(e["expected_intent"] for e in golden_data)
    decision_dist = Counter(e["expected_decision"] for e in golden_data)
    diff_dist = Counter(e["difficulty"] for e in golden_data)
    
    print("\n--- GOLDEN SET INTENT DISTRIBUTION ---")
    for k, v in intent_dist.items():
        print(f"  {k}: {v} ({v/len(golden_data)*100:.1f}%)")
        
    print("\n--- GOLDEN SET DECISION DISTRIBUTION ---")
    for k, v in decision_dist.items():
        print(f"  {k}: {v} ({v/len(golden_data)*100:.1f}%)")

    print("\n--- GOLDEN SET DIFFICULTY DISTRIBUTION ---")
    for k, v in diff_dist.items():
        print(f"  {k}: {v} ({v/len(golden_data)*100:.1f}%)")

    filepath = output_dir / "golden_eval_set.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(golden_data, f, indent=2)
        
    print(f"\nGolden evaluation set saved to {filepath}")

if __name__ == "__main__":
    main()
