---
type: client-manifest
subject: <Client name>
folder: <Client-folder-name>
status: active  # active | dormant | archived
last-updated: YYYY-MM-DD
maintainer: <Name>
purpose: Lookup index for matching transcripts and communications to this client. Used by the client-brief-processor skill (and any other skill that needs to route input to a specific client) to identify which client a piece of input belongs to.
---

# <Client name> — Client Manifest

> **Purpose:** This file is a lookup index. When an agent receives a transcript, email, or other communication, it scans for the keywords, names, and domains listed below to determine which client the input belongs to. Keep this file current — add new contacts, aliases, and project keywords as they emerge.

## Company identifiers

| Keyword | Match type |
|---|---|
| <Full company name> | company name |
| <Common abbreviation> | abbreviation |
| <Domain> | email domain |

> Add every plausible way someone might refer to this company: full name, abbreviations, common misspellings, domain names. Include subsidiary and brand names if they might appear in transcripts instead of the parent company name.

## Contact identifiers

| Name | Email | Role |
|---|---|---|
| <Name> | <email> | <Role> |

> One row per contact who has materially shown up in our work with this client. These are the names that, when they appear in a transcript, should route to this client. Update as new contacts emerge.

## Business unit identifiers (if applicable)

Subsidiaries, brands, or divisions that may appear in transcripts as the "client" but route to this parent client:

| BU name | Domain | Notes |
|---|---|---|
| <BU name> | <domain> | <context> |

> Remove this section if not applicable (e.g., for companies without subsidiaries).

## Project identifiers

Keywords that may appear in transcripts and indicate this client:

| Keyword | Context |
|---|---|
| <Project/product name> | <Brief context> |

> Add project names, product names, internal initiative names, and any other keywords that would uniquely identify this client's work. Update as new projects start.

## Notes

> Any routing quirks, ambiguities, or special handling instructions. For example: "This client was previously called X — transcripts may use either name" or "The 'Acme' BU has its own domain (acme.com) but routes to the parent client."
