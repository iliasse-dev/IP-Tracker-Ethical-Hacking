#!/usr/bin/env python3
"""
IP Tracker - IP geolocation tool with a Kali-style terminal interface.

Look up your own public IP or any other IP address and get location,
network and timezone information.

Requirements:  pip install requests pyfiglet colorama

For educational and ethical use only.
(c) 2026 All rights reserved - By Iliasse Dev </>
"""

import ipaddress
import os
import sys
import time

import pyfiglet
import requests
from colorama import Fore, Style, init

init(autoreset=True)

# ---------- colors ----------
GREEN = Fore.GREEN + Style.BRIGHT
DIM_GREEN = Fore.GREEN
CYAN = Fore.CYAN + Style.BRIGHT
RED = Fore.RED + Style.BRIGHT
YELLOW = Fore.YELLOW + Style.BRIGHT
WHITE = Fore.WHITE + Style.BRIGHT
GREY = Fore.WHITE + Style.DIM
RESET = Style.RESET_ALL

API_URL = "https://ipwho.is/"
WIDTH = 64


# ---------- terminal helpers ----------
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def banner():
    clear_screen()
    art = pyfiglet.figlet_format("IP TRACKER", font="slant")
    print(GREEN + art)
    print(DIM_GREEN + "=" * WIDTH)
    print(CYAN + "  IP Geolocation & Network Recon Tool")
    print(GREY + "  v1.0  |  Ethical use only  |  By Iliasse Dev </>")
    print(DIM_GREEN + "=" * WIDTH + "\n")


def prompt(label="geo"):
    """Kali-like two line prompt."""
    print(f"{GREEN}┌──({CYAN}iliasse{GREEN}㉿{CYAN}{label}{GREEN})-[{WHITE}~{GREEN}]")
    return input(f"{GREEN}└─{CYAN}${RESET} ").strip()


def info(msg):
    print(f"{CYAN}[*]{RESET} {msg}")


def good(msg):
    print(f"{GREEN}[+]{RESET} {msg}")


def warn(msg):
    print(f"{YELLOW}[!]{RESET} {msg}")


def error(msg):
    print(f"{RED}[-]{RESET} {msg}")


def loading(text, seconds=1.4):
    """Small scanning animation."""
    frames = ["|", "/", "-", "\\"]
    end = time.time() + seconds
    i = 0
    while time.time() < end:
        sys.stdout.write(f"\r{CYAN}[{frames[i % 4]}]{RESET} {text}")
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    sys.stdout.write("\r" + " " * (len(text) + 10) + "\r")


# ---------- main logic ----------
def is_valid_ip(value):
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False


def is_public_ip(value):
    ip = ipaddress.ip_address(value)
    return not (ip.is_private or ip.is_loopback or ip.is_reserved
                or ip.is_link_local or ip.is_multicast)


def fetch_ip_info(ip=""):
    """Ask the API about an IP. Empty string = our own public IP."""
    try:
        response = requests.get(API_URL + ip, timeout=8)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        error("No internet connection.")
    except requests.exceptions.Timeout:
        error("The request timed out. Try again.")
    except requests.exceptions.RequestException as e:
        error(f"Request failed: {e}")
    except ValueError:
        error("The server sent an invalid response.")
    return None


def row(label, value):
    value = value if value not in (None, "", []) else "N/A"
    print(f"{DIM_GREEN}│{RESET} {CYAN}{label:<15}{RESET}{GREEN}:{RESET} {WHITE}{value}")


def section(title):
    print(f"{DIM_GREEN}├─[ {GREEN}{title}{DIM_GREEN} ]{'─' * (WIDTH - len(title) - 6)}")


def show_report(data):
    connection = data.get("connection", {})
    timezone = data.get("timezone", {})
    lat = data.get("latitude")
    lon = data.get("longitude")

    print()
    print(f"{DIM_GREEN}┌{'─' * (WIDTH - 1)}")
    print(f"{DIM_GREEN}│ {GREEN}TARGET REPORT")

    section("IDENTITY")
    row("IP Address", data.get("ip"))
    row("IP Version", data.get("type"))

    section("LOCATION")
    row("Country", f"{data.get('country')} ({data.get('country_code')})")
    row("Continent", data.get("continent"))
    row("Region", data.get("region"))
    row("City", data.get("city"))
    row("Postal Code", data.get("postal"))
    row("Capital", data.get("capital"))
    row("Latitude", lat)
    row("Longitude", lon)
    if lat is not None and lon is not None:
        row("Google Maps", f"https://www.google.com/maps?q={lat},{lon}")

    section("NETWORK")
    row("ISP", connection.get("isp"))
    row("Organization", connection.get("org"))
    row("ASN", f"AS{connection.get('asn')}" if connection.get("asn") else None)
    row("Domain", connection.get("domain"))

    section("TIMEZONE")
    row("Zone", timezone.get("id"))
    row("UTC Offset", timezone.get("utc"))
    row("Local Time", timezone.get("current_time"))

    print(f"{DIM_GREEN}└{'─' * (WIDTH - 1)}\n")


def lookup(ip=""):
    target = ip if ip else "your public IP"
    info(f"Target: {WHITE}{target}")
    loading("Querying geolocation database...")

    data = fetch_ip_info(ip)
    if data is None:
        return

    if not data.get("success", False):
        error(f"Lookup failed: {data.get('message', 'unknown error')}")
        return

    good("Target located successfully.")
    show_report(data)


def menu():
    print(f"{GREEN}[{WHITE}1{GREEN}]{RESET} Track my own IP")
    print(f"{GREEN}[{WHITE}2{GREEN}]{RESET} Track another IP address")
    print(f"{GREEN}[{WHITE}3{GREEN}]{RESET} Clear screen")
    print(f"{GREEN}[{WHITE}0{GREEN}]{RESET} Exit\n")


def ask_for_ip():
    ip = prompt("target")
    if not is_valid_ip(ip):
        error("That is not a valid IPv4 or IPv6 address.")
        return None
    if not is_public_ip(ip):
        warn("This is a private or reserved address. It can't be geolocated.")
        return None
    return ip


def main():
    banner()
    warn("Only look up IP addresses you are allowed to investigate.\n")

    while True:
        menu()
        choice = prompt()
        print()

        if choice == "1":
            lookup()
        elif choice == "2":
            info("Enter the IP address to track:")
            ip = ask_for_ip()
            if ip:
                lookup(ip)
        elif choice == "3":
            banner()
            continue
        elif choice == "0":
            good("Session closed. Stay ethical.")
            break
        else:
            error("Invalid option. Choose 1, 2, 3 or 0.")

        input(f"{GREY}Press Enter to continue...{RESET}")
        banner()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{RED}[!]{RESET} Interrupted. Bye.")
        sys.exit(0)