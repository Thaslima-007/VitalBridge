# VitalBridge

VitalBridge is an academic web-application prototype for a wearable-assisted wellbeing monitoring concept for individuals with Autism Spectrum Disorder (ASD) and Intellectual and Developmental Disabilities (IDD), with views for both individuals and caregivers.

## Current prototype features

- Role selection: caregiver or individual demo view
- Dashboard with simulated heart rate, body temperature and SpO2 readings
- Demo status levels: Normal, Warning and Emergency
- Generate normal, warning and emergency sample scenarios
- Recent activity / alert history stored in SQLite
- Caregiver-only acknowledge action
- Responsive web interface

## Important safety and scope notice

This project currently uses **simulated data only**. It is not a medical device, diagnostic tool, validated monitoring system, or emergency service. The thresholds in `app.py` are demonstration values only and must not be used for medical decisions. Do not enter real patient data. GPS, real wearable sensors, SMS/push alerts, secure user accounts and clinical validation are not implemented in this prototype.

## Requirements

- Python 3.10 or newer
- pip

## Run locally

1. Download or clone this repository.
2. Open a terminal in the project folder.
3. Create a virtual environment:

   ```bash
   python -m venv .venv
   ```

4. Activate it:

   **Windows PowerShell**
   ```powershell
   .venv\Scripts\Activate.ps1
   ```

   **macOS / Linux**
   ```bash
   source .venv/bin/activate
   ```

5. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

6. Start the app:

   ```bash
   python app.py
   ```

7. Open `http://127.0.0.1:5000` in your browser.

## Project structure

```text
VitalBridge/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── templates/
│   ├── index.html
│   └── dashboard.html
└── static/
    ├── app.js
    └── style.css
```

## Demo walkthrough

1. Open the home page and choose Caregiver or Individual.
2. Generate a normal sample.
3. Select **Test warning** to create a warning example.
4. Select **Test emergency** to create an emergency example.
5. In the caregiver view, acknowledge an alert in Recent activity.
6. Log out and open the Individual view to see the individual-facing dashboard.

## Future development

- Integrate validated wearable sensors through a suitable device gateway
- Add per-individual baseline configuration with caregiver consent
- Add secure authentication, authorization and audit logging
- Add privacy controls and data-retention policy
- Add GPS only with informed consent and appropriate safeguards
- Add notification delivery after reliability, safety and privacy testing
- Conduct usability testing with individuals, caregivers and domain professionals

## License

This project is released under the MIT License. See `LICENSE`.
