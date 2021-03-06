#!/usr/bin/env python3

import os
import sys
import re
import colored
import requests
import whois

BOLD = colored.attr("bold")
RESET = colored.attr("reset")
RED = colored.fg("red")
GREEN = colored.fg("green")
ORANGE = colored.fg("yellow")
CYAN = colored.fg("light_cyan")

# --------------------------------------------------------------------------- #
# Gets all valid domains created by bit-flipping one byte of a given domain
def check(domain, silent=False):
    tlds = validTLDs()
    if not validDomain(domain, tlds):
        raise ValueError
    bits = textToBits(domain)
    results = []

    apiKey = tryReadingAPIKey()

    for i in range(len(bits)):
        if bits[i] == "0":
            bit = "1"
        else:
            bit = "0"
        flipped = bits[:i] + bit + bits[i+1:]
        try:
            results.append(bitsToText(flipped))
        except UnicodeDecodeError:
            pass

    results = [result.lower() for result in results]
    results = [result for result in results if result != domain]
    results = [result for result in results if validDomain(result, tlds)]
    if not silent:
        for result in set(results):
            if apiKey:
                domainStatus = getDomainStatus(result, apiKey)
                print(BOLD + CYAN + result + RESET + ": " + domainStatus)
            else:
                print(result)

    return results
# ########################################################################### #


# --------------------------------------------------------------------------- #
# Converts ASCII string to bit string
def textToBits(text):
    bits  = str(bin(int.from_bytes(text.encode(), 'big')))[2:]
    return bits.zfill(8 * ((len(bits) + 7) // 8))
# ########################################################################### #


# --------------------------------------------------------------------------- #
# Converts bit string to ASCII string
def bitsToText(bits):
    text = int(bits, 2)
    return text.to_bytes((text.bit_length() + 7) // 8, 'big').decode()
# ########################################################################### #


# --------------------------------------------------------------------------- #
# Checks if string fullfills all the requirements of a domain name
def validDomain(text, tlds):
    #Whitespace in domains is not allowed
    if " " in text:
        return False

    #Valid domain can't being or end with a hyphen
    if not "." in text:
        return False

    #Valid domain can't being or end with a hyphen
    if text[0] == "-" or text[-1] == "-":
        return False

    #Valid domain can't have a hyphen before or after dot
    dots = [m.start() for m in re.finditer('\.', text)]
    for dot in dots:
        if "-" in text[dot-1:dot+1]:
            return False

    #Domain ending must be on list of valid TLDs
    if not text[dots[-1]+1:] in tlds:
        return False

    if text[text.rfind(".")-1] == "-":
        return False
    return not bool(re.compile(r'[^a-z0-9.]').search(text))
# ########################################################################### #


# --------------------------------------------------------------------------- #
# Queries domainr to get registration status of domain
def getDomainStatus(domain, apiKey):
    url = "https://domainr.p.mashape.com/v2/status?mashape-key="+apiKey+"&domain="+domain
    r = requests.get(url)
    try:
        status = r.json()["status"][0]["status"]
    except KeyError:
        status = "unknown"

    if "inactive" in status:
        status = BOLD + GREEN + "Available" + RESET
    elif "active" in status:
        status = BOLD + RED + "Taken" + RESET
        w = whois.whois(domain)
        name = w.name
        if isinstance(name, list):
            name = name[0]
        expDate = w.expiration_date
        if isinstance(expDate, list):
            expDate = expDate[0]
        if name and expDate:
            status += " (Reg: " + BOLD + name + RESET + ", exp: " + BOLD + expDate.strftime("%Y-%m-%d") + RESET + ")"
        elif name:
            status += " (Reg: " + BOLD + name + RESET + ")"
        elif expDate:
            status += " (Exp: " + BOLD + expDate.strftime("%Y-%m-%d") + RESET + ")"
    else:
        status = BOLD + ORANGE + "Unknown" + RESET
    return status
# ########################################################################### #


# --------------------------------------------------------------------------- #
# Reads list of all valid TLDs from a file provided by IANA:
#   https://data.iana.org/TLD/tlds-alpha-by-domain.txt
def validTLDs():
    tlds = []

    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "tlds.txt")) as f:
        for line in f:
            if not line.startswith("#"):
                tlds.append(line.rstrip().lower())

    return tlds
# ########################################################################### #


# --------------------------------------------------------------------------- #
# Checks if a domainr/mashape API Key is available
def tryReadingAPIKey():
    try:
        with open(os.path.join(os.path.expanduser("~"), ".bitflipper")) as f:
            for line in f:
                if line.startswith("DOMAINR-API"):
                    return line[line.rfind("=")+1:].rstrip()
            return ""
    except Exception:
        return ""
# ########################################################################### #


# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    try:
        check(sys.argv[1])
    except (IndexError, KeyError, ValueError):
        print("Please specify a valid domain to test!\nTry: bitflipper example.com")
    except IOError:
        print("Unable to load valid TLDs")
    except KeyboardInterrupt:
        print("Aborted!")
# ########################################################################### #
