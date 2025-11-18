BOT_TOKEN = "7739260475:AAEyHo47ABQ9kOAXMs8_zfN30-0k2F6cLbk"
REQUEST_TIMEOUT = 800

# Security settings
COOLDOWN_SECONDS = 25  # 25 seconds between card checks
OWNER_USER_ID = 6302946121 # SOSTITUISCI CON IL TUO USER ID
ALLOWED_GROUP_ID = 5942119331
ALLOWED_CHAT_IDS = [5942119331]

# API Endpoints
API_ENDPOINTS = {
    'stripe1': "http://135.148.14.197:5000/stripe1$?cc=",
    'stripe5': "http://135.148.14.197:5000/stripe5$?cc=",
    'shopify': "http://135.148.14.197:5000/shopify1$?cc=",
    'authnet': "http://135.148.14.197:5000/authnet1$?cc=",
    'crunchyroll': "http://135.148.14.197:8000/crunchyroll?email=",
    'bin_lookup': "https://drlabapis.onrender.com/api/bin?bin=",
    'cc_generator': "https://drlabapis.onrender.com/api/ccgenerator?bin="

}
