def detect_fraud(name: str, email: str, phone: str, message: str) -> dict:
    """Detect potential fraud/spam"""
    
    signals = []
    
    # Disposable email check
    disposable_domains = [
        'tempmail.com', '10minutemail.com', 'guerrillamail.com',
        'throwaway.email', 'mailinator.com', 'trashmail.com'
    ]
    email_domain = email.split('@')[1].lower() if '@' in email else ''
    if email_domain in disposable_domains:
        signals.append('Disposable email')
    
    # Phone validation
    phone_clean = ''.join(filter(str.isdigit, phone))
    if len(set(phone_clean)) == 1:
        signals.append('Repeated digits')
    if len(phone_clean) < 10:
        signals.append('Phone too short')
    
    # Name validation
    if any(word in name.lower() for word in ['test', 'demo', 'asdf', 'admin']):
        signals.append('Generic name')
    if len(name) < 3:
        signals.append('Name too short')
    
    # Message validation
    if len(message) < 10:
        signals.append('Message too short')
    
    is_fraud = len(signals) >= 2
    
    return {'is_fraud': is_fraud, 'signals': signals}