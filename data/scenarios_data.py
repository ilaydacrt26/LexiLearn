SCENARIOS = {
    "A1": {
        "restaurant": {
            "title": "Restoranda Yemek Sipariş Etmek",
            "description": "Restoranda garsonla konuşup yemek sipariş ediyorsunuz.",
            "vocabulary": ["menu", "order", "please", "thank you", "bill", "water"],
            "phrases": [
                "Can I see the menu, please?",
                "I would like to order...",
                "Can I have the bill, please?",
                "Thank you very much."
            ],
            "dialogue_flow": [
                {"speaker": "waiter", "text": "Good evening! Welcome to our restaurant. Here is the menu."},
                {"speaker": "user", "expected": "greeting and menu request"},
                {"speaker": "waiter", "text": "What would you like to order?"},
                {"speaker": "user", "expected": "food order"},
                {"speaker": "waiter", "text": "Would you like something to drink?"},
                {"speaker": "user", "expected": "drink order"},
                {"speaker": "waiter", "text": "Your food will be ready in 15 minutes."},
                {"speaker": "user", "expected": "acknowledgment"}
            ]
        },
        "hotel": {
            "title": "Otelde Resepsiyonla Konuşmak",
            "description": "Otele giriş yaparken resepsiyonist ile konuşuyorsunuz.",
            "vocabulary": ["reservation", "room", "key", "passport", "breakfast"],
            "phrases": [
                "I have a reservation.",
                "Can I have my room key, please?",
                "Is breakfast included?",
                "Thank you!"
            ],
            "dialogue_flow": [
                {"speaker": "receptionist", "text": "Hello! Welcome. Do you have a reservation?"},
                {"speaker": "user", "expected": "state reservation"},
                {"speaker": "receptionist", "text": "Can I see your passport, please?"},
                {"speaker": "user", "expected": "give passport"},
                {"speaker": "receptionist", "text": "Here is your room key. Breakfast is from 7 to 10."},
                {"speaker": "user", "expected": "thank and acknowledge"}
            ]
        },
        "directions": {
            "title": "Yol Tarifi Sormak",
            "description": "Yolda birine yol soruyorsunuz.",
            "vocabulary": ["where", "turn", "left", "right", "street", "go straight"],
            "phrases": [
                "Excuse me, where is the bank?",
                "Turn left at the corner.",
                "Go straight ahead.",
                "Thank you for your help!"
            ],
            "dialogue_flow": [
                {"speaker": "user", "expected": "ask for location"},
                {"speaker": "stranger", "text": "Go straight and turn right at the traffic lights."},
                {"speaker": "user", "expected": "repeat or confirm directions"},
                {"speaker": "stranger", "text": "Yes, it's next to the supermarket."},
                {"speaker": "user", "expected": "thank and goodbye"}
            ]
        },
        "market": {
            "title": "Pazarda Meyve Sebze Almak",
            "description": "Pazarda satıcıdan meyve veya sebze alıyorsunuz.",
            "vocabulary": ["apple", "banana", "tomato", "price", "how much", "kilo"],
            "phrases": [
                "How much is this?",
                "I would like one kilo of tomatoes.",
                "Can I have three apples, please?",
                "Thank you!"
            ],
            "dialogue_flow": [
                {"speaker": "seller", "text": "Hello! What would you like today?"},
                {"speaker": "user", "expected": "state product request"},
                {"speaker": "seller", "text": "It’s 2 euros per kilo."},
                {"speaker": "user", "expected": "confirm amount"},
                {"speaker": "seller", "text": "Here you go."},
                {"speaker": "user", "expected": "thank and pay"}
            ]
        }
    },
    "A2": {
        "shopping": {
            "title": "Kıyafet Alışverişi",
            "description": "Bir mağazada kıyafet satın alıyorsunuz.",
            "vocabulary": ["size", "try on", "price", "fitting room", "color", "buy"],
            "phrases": [
                "Can I try this on?",
                "Do you have this in size M?",
                "How much is it?",
                "I’ll take it, thank you!"
            ],
            "dialogue_flow": [
                {"speaker": "shop_assistant", "text": "Hello! Can I help you?"},
                {"speaker": "user", "expected": "ask for item or size"},
                {"speaker": "shop_assistant", "text": "Yes, the fitting rooms are over there."},
                {"speaker": "user", "expected": "ask about price or buy decision"},
                {"speaker": "shop_assistant", "text": "It’s 25 euros."},
                {"speaker": "user", "expected": "confirm purchase"}
            ]
        },
        "pharmacy": {
            "title": "Eczanede İlaç Almak",
            "description": "Bir sağlık problemi için eczanede ilaç istiyorsunuz.",
            "vocabulary": ["medicine", "headache", "pain", "prescription", "how often"],
            "phrases": [
                "I have a headache.",
                "Do I need a prescription?",
                "How often should I take it?",
                "Thank you!"
            ],
            "dialogue_flow": [
                {"speaker": "pharmacist", "text": "Hello, how can I help you?"},
                {"speaker": "user", "expected": "describe problem"},
                {"speaker": "pharmacist", "text": "You can take this medicine twice a day."},
                {"speaker": "user", "expected": "ask about dosage or prescription"},
                {"speaker": "pharmacist", "text": "No prescription needed."},
                {"speaker": "user", "expected": "thank"}
            ]
        },
        "post_office": {
            "title": "Postanede Paket Göndermek",
            "description": "Bir paketi postaneden gönderiyorsunuz.",
            "vocabulary": ["send", "package", "address", "post", "delivery", "stamp"],
            "phrases": [
                "I’d like to send this package.",
                "How much is the delivery?",
                "Do I need a stamp?",
                "Here’s the address."
            ],
            "dialogue_flow": [
                {"speaker": "clerk", "text": "Hello! What can I do for you?"},
                {"speaker": "user", "expected": "state sending request"},
                {"speaker": "clerk", "text": "Where would you like to send it?"},
                {"speaker": "user", "expected": "give address"},
                {"speaker": "clerk", "text": "It will cost 10 euros."},
                {"speaker": "user", "expected": "confirm and pay"}
            ]
        }
    },
    "B1": {
        "job_interview": {
            "title": "İş Görüşmesi",
            "description": "Bir iş görüşmesinde kendinizi tanıtıyorsunuz.",
            "vocabulary": ["experience", "skills", "strengths", "teamwork", "responsibility"],
            "phrases": [
                "I have three years of experience in marketing.",
                "I’m a team player.",
                "I’m good at problem-solving.",
                "Thank you for the opportunity."
            ],
            "dialogue_flow": [
                {"speaker": "interviewer", "text": "Welcome! Can you tell me about yourself?"},
                {"speaker": "user", "expected": "self-introduction"},
                {"speaker": "interviewer", "text": "What are your strengths?"},
                {"speaker": "user", "expected": "describe strengths"},
                {"speaker": "interviewer", "text": "Why do you want to work with us?"},
                {"speaker": "user", "expected": "state motivation"},
                {"speaker": "interviewer", "text": "Thank you for coming today."},
                {"speaker": "user", "expected": "thank and goodbye"}
            ]
        },
        "complaint": {
            "title": "Şikayet Etmek",
            "description": "Bir ürün veya hizmet hakkında şikayette bulunuyorsunuz.",
            "vocabulary": ["complain", "broken", "refund", "exchange", "not working"],
            "phrases": [
                "I’d like to make a complaint.",
                "This item is broken.",
                "Can I get a refund or exchange?",
                "I’m not happy with this service."
            ],
            "dialogue_flow": [
                {"speaker": "user", "expected": "state complaint"},
                {"speaker": "staff", "text": "I’m sorry to hear that. What’s the problem?"},
                {"speaker": "user", "expected": "describe issue"},
                {"speaker": "staff", "text": "Would you like a refund or exchange?"},
                {"speaker": "user", "expected": "choose option"},
                {"speaker": "staff", "text": "We’ll process that right away."}
            ]
        },
        "university": {
            "title": "Üniversite Kaydı",
            "description": "Bir üniversiteye kayıt için öğrenci işleriyle konuşuyorsunuz.",
            "vocabulary": ["enroll", "application", "documents", "deadline", "course"],
            "phrases": [
                "I’d like to enroll in this course.",
                "What documents do I need?",
                "When is the application deadline?",
                "Thank you for the information."
            ],
            "dialogue_flow": [
                {"speaker": "officer", "text": "Hello, how can I help you?"},
                {"speaker": "user", "expected": "state enrollment request"},
                {"speaker": "officer", "text": "You need to fill out this form and bring your ID."},
                {"speaker": "user", "expected": "ask about deadline"},
                {"speaker": "officer", "text": "The deadline is next Friday."},
                {"speaker": "user", "expected": "thank and confirm understanding"}
            ]
        }
    },
    "B2": {
        "social_issues": {
            "title": "Toplumsal Konuları Tartışmak",
            "description": "Bir arkadaşınızla çevre sorunları üzerine konuşuyorsunuz.",
            "vocabulary": ["environment", "pollution", "global warming", "recycling", "sustainable"],
            "phrases": [
                "Climate change is a serious problem.",
                "We should reduce plastic usage.",
                "Sustainable living is important.",
                "I totally agree with you."
            ],
            "dialogue_flow": [
                {"speaker": "friend", "text": "What do you think about global warming?"},
                {"speaker": "user", "expected": "state opinion"},
                {"speaker": "friend", "text": "Do you do anything to help the environment?"},
                {"speaker": "user", "expected": "describe actions"},
                {"speaker": "friend", "text": "That's great! More people should do that."},
                {"speaker": "user", "expected": "agree or suggest ideas"}
            ]
        },
        "business_trip": {
            "title": "İş Seyahati Rezervasyonu",
            "description": "Bir iş seyahati için uçak ve otel rezervasyonu yapıyorsunuz.",
            "vocabulary": ["book", "flight", "accommodation", "departure", "return", "schedule"],
            "phrases": [
                "I’d like to book a round-trip flight to Berlin.",
                "I need a hotel near the city center.",
                "My departure date is next Monday.",
                "Is breakfast included in the hotel?"
            ],
            "dialogue_flow": [
                {"speaker": "agent", "text": "How can I help you today?"},
                {"speaker": "user", "expected": "state travel request"},
                {"speaker": "agent", "text": "When would you like to depart and return?"},
                {"speaker": "user", "expected": "give dates"},
                {"speaker": "agent", "text": "I found a flight and a 4-star hotel nearby."},
                {"speaker": "user", "expected": "confirm booking or ask questions"}
            ]
        },
        "debate": {
            "title": "Bir Konu Üzerine Münazara",
            "description": "Bir arkadaşınızla teknoloji bağımlılığı üzerine münazara yapıyorsunuz.",
            "vocabulary": ["addiction", "social media", "balance", "negative effects", "mental health"],
            "phrases": [
                "Technology has both advantages and disadvantages.",
                "Too much screen time is harmful.",
                "We need to find a balance.",
                "I understand your point, but I disagree."
            ],
            "dialogue_flow": [
                {"speaker": "friend", "text": "Do you think technology is making people less social?"},
                {"speaker": "user", "expected": "state opinion"},
                {"speaker": "friend", "text": "But it also helps people connect online."},
                {"speaker": "user", "expected": "acknowledge and give counterpoint"},
                {"speaker": "friend", "text": "Maybe a balance is the solution."},
                {"speaker": "user", "expected": "agree and suggest how"}
            ]
        }
    }
}
