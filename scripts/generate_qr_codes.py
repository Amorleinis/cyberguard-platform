"""
Generate QR Codes for GitHub Repositories
Creates downloadable QR codes for each engine package repository
"""

import qrcode
from pathlib import Path

# Repository URLs
repos = {
    "intelligence": {
        "url": "https://github.com/Amorleinis/threat-intelligence-engine",
        "name": "Intelligence Engine"
    },
    "prevention": {
        "url": "https://github.com/Amorleinis/threat-prevention-engine",
        "name": "Prevention Engine"
    },
    "detection": {
        "url": "https://github.com/Amorleinis/threat-detection-engine",
        "name": "Detection Engine"
    },
    "response": {
        "url": "https://github.com/Amorleinis/incident-response-engine",
        "name": "Response Engine"
    },
    "isolation": {
        "url": "https://github.com/Amorleinis/threat-isolation-engine",
        "name": "Isolation Engine"
    },
    "mitigation": {
        "url": "https://github.com/Amorleinis/threat-mitigation-engine",
        "name": "Mitigation Engine"
    },
    "recovery": {
        "url": "https://github.com/Amorleinis/system-recovery-engine",
        "name": "Recovery Engine"
    }
}

def generate_qr_code(url, output_path, name):
    """Generate QR code for a URL"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(output_path)
    print(f"✓ Generated QR code for {name}: {output_path}")

def main():
    print("=" * 80)
    print("GENERATING QR CODES FOR GITHUB REPOSITORIES")
    print("=" * 80)
    print()
    
    # Create QR codes for each engine
    for engine, info in repos.items():
        engine_dir = Path(engine)
        qr_path = engine_dir / "repository_qr.png"
        
        if engine_dir.exists():
            generate_qr_code(info["url"], qr_path, info["name"])
    
    print()
    print("=" * 80)
    print("QR CODES GENERATED SUCCESSFULLY")
    print("=" * 80)
    print()
    print("QR codes saved to each engine folder as 'repository_qr.png'")
    print("Users can scan these to quickly access the GitHub repositories!")
    print()
    print("Next steps:")
    print("  1. Add QR codes to README.md files")
    print("  2. Include in documentation")
    print("  3. Use in presentations or posters")
    print()

if __name__ == "__main__":
    main()
