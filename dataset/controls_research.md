# Cybersecurity-Relevant Controls in Three Biotech Compliance Frameworks

**A citable control catalog for the CyberBio benchmark**

- Scope: (1) HIPAA Security Rule: 45 CFR Part 164, Subpart C; (2) FDA 21 CFR Part 11 (Electronic Records; Electronic Signatures); (3) GxP data integrity for computerised systems: ALCOA+, EU GMP Annex 11, and ISPE GAMP 5 (2nd ed.).
- Compiled: 2026-08-10.
- Verification method: regulatory text verified verbatim against primary sources: Cornell Law LII mirror of the U.S. Code of Federal Regulations for the CFR material, and the official European Commission EudraLex Volume 4 PDF for Annex 11. ALCOA+ and GAMP 5 details are cross-checked against regulator guidance and ISPE publication metadata; where a source is secondary (paywalled ISPE guide), it is flagged explicitly in the Sources section and in the relevant rows.
- Notation: For HIPAA, each implementation specification is tagged **(Required)** or **(Addressable)** exactly as it appears in the rule; the parent "standards" are always mandatory but carry no R/A tag (marked "Standard"). 21 CFR Part 11 and Annex 11 requirements are all mandatory within their applicability scope (no R/A distinction); ALCOA+ are principles, not clauses.
- Normalized families (used in the last column of every table and defined in Part B):
  AC = Access Control & Authorization · IA = Identity & Authentication · AU = Audit Trail & Logging · EN = Encryption & Transmission Security · DI = Data Integrity & Non-repudiation · BK = Backup, Availability & Contingency · CV = Configuration, Validation & Change Control · SM = Security Management, Risk & Incident Response.

---

## Part A: Per-Framework Control Extraction

### A.1 HIPAA Security Rule: 45 CFR Part 164, Subpart C

Legal structure: three safeguard groups (Administrative §164.308, Physical §164.310, Technical §164.312), each composed of *standards* and, under many, *implementation specifications* that are either **Required** or **Addressable**. "Addressable" does not mean optional: the covered entity/business associate must assess whether the specification is reasonable and appropriate, implement it if so, or document why not and implement an equivalent alternative (§164.306(d)).

#### A.1.1 Technical Safeguards: §164.312

| control_id | Official citation | Title | Cyber requirement (paraphrase) | R/A | Family |
|---|---|---|---|---|---|
| HIPAA-312-a-1 | 45 CFR 164.312(a)(1) | Access control (standard) | Implement technical policies/procedures for systems holding ePHI so that only persons or software programs granted access rights can obtain access. | Standard | AC |
| HIPAA-312-a-2-i | 45 CFR 164.312(a)(2)(i) | Unique user identification | Assign a unique name and/or number for identifying and tracking user identity. | Required | IA |
| HIPAA-312-a-2-ii | 45 CFR 164.312(a)(2)(ii) | Emergency access procedure | Establish (and implement as needed) procedures for obtaining necessary ePHI during an emergency. | Required | AC |
| HIPAA-312-a-2-iii | 45 CFR 164.312(a)(2)(iii) | Automatic logoff | Electronic procedures that terminate an electronic session after a predetermined time of inactivity. | Addressable | AC |
| HIPAA-312-a-2-iv | 45 CFR 164.312(a)(2)(iv) | Encryption and decryption | Implement a mechanism to encrypt and decrypt ePHI (at rest). | Addressable | EN |
| HIPAA-312-b | 45 CFR 164.312(b) | Audit controls | Implement hardware, software, and/or procedural mechanisms that record and examine activity in information systems that contain or use ePHI. | Standard | AU |
| HIPAA-312-c-1 | 45 CFR 164.312(c)(1) | Integrity (standard) | Implement policies/procedures to protect ePHI from improper alteration or destruction. | Standard | DI |
| HIPAA-312-c-2 | 45 CFR 164.312(c)(2) | Mechanism to authenticate ePHI | Implement electronic mechanisms to corroborate that ePHI has not been altered or destroyed in an unauthorized manner. | Addressable | DI |
| HIPAA-312-d | 45 CFR 164.312(d) | Person or entity authentication | Implement procedures to verify that a person or entity seeking access to ePHI is the one claimed. | Standard | IA |
| HIPAA-312-e-1 | 45 CFR 164.312(e)(1) | Transmission security (standard) | Implement technical security measures to guard against unauthorized access to ePHI transmitted over an electronic communications network. | Standard | EN |
| HIPAA-312-e-2-i | 45 CFR 164.312(e)(2)(i) | Integrity controls | Ensure transmitted ePHI is not improperly modified without detection until disposed of. | Addressable | EN |
| HIPAA-312-e-2-ii | 45 CFR 164.312(e)(2)(ii) | Encryption (in transit) | Implement a mechanism to encrypt ePHI whenever deemed appropriate. | Addressable | EN |

#### A.1.2 Administrative Safeguards: §164.308 (cyber-relevant subset)

| control_id | Official citation | Title | Cyber requirement (paraphrase) | R/A | Family |
|---|---|---|---|---|---|
| HIPAA-308-a-1-i | 45 CFR 164.308(a)(1)(i) | Security management process (standard) | Implement policies/procedures to prevent, detect, contain, and correct security violations. | Standard | SM |
| HIPAA-308-a-1-ii-A | 45 CFR 164.308(a)(1)(ii)(A) | Risk analysis | Conduct an accurate and thorough assessment of the potential risks and vulnerabilities to the confidentiality, integrity, and availability of ePHI. | Required | SM |
| HIPAA-308-a-1-ii-B | 45 CFR 164.308(a)(1)(ii)(B) | Risk management | Implement security measures sufficient to reduce risks and vulnerabilities to a reasonable and appropriate level. | Required | SM |
| HIPAA-308-a-1-ii-C | 45 CFR 164.308(a)(1)(ii)(C) | Sanction policy | Apply appropriate sanctions against workforce members who fail to comply with security policies/procedures. | Required | SM |
| HIPAA-308-a-1-ii-D | 45 CFR 164.308(a)(1)(ii)(D) | Information system activity review | Regularly review records of information system activity (audit logs, access reports, security incident tracking reports). | Required | AU |
| HIPAA-308-a-2 | 45 CFR 164.308(a)(2) | Assigned security responsibility (standard) | Identify the security official responsible for developing/implementing the required policies and procedures. | Standard | SM |
| HIPAA-308-a-3-i | 45 CFR 164.308(a)(3)(i) | Workforce security (standard) | Ensure all workforce members have appropriate ePHI access and prevent those without authorization from obtaining access. | Standard | AC |
| HIPAA-308-a-3-ii-A | 45 CFR 164.308(a)(3)(ii)(A) | Authorization and/or supervision | Authorize/supervise workforce members who work with ePHI or in locations where it may be accessed. | Addressable | AC |
| HIPAA-308-a-3-ii-B | 45 CFR 164.308(a)(3)(ii)(B) | Workforce clearance procedure | Determine that a workforce member's access to ePHI is appropriate. | Addressable | AC |
| HIPAA-308-a-3-ii-C | 45 CFR 164.308(a)(3)(ii)(C) | Termination procedures | Terminate access to ePHI when employment/authorization ends. | Addressable | AC |
| HIPAA-308-a-4-i | 45 CFR 164.308(a)(4)(i) | Information access management (standard) | Implement policies/procedures for authorizing access to ePHI consistent with the minimum-necessary requirements. | Standard | AC |
| HIPAA-308-a-4-ii-A | 45 CFR 164.308(a)(4)(ii)(A) | Isolating health care clearinghouse functions | A clearinghouse that is part of a larger organization must protect ePHI from the rest of the organization. | Required | AC |
| HIPAA-308-a-4-ii-B | 45 CFR 164.308(a)(4)(ii)(B) | Access authorization | Grant access to ePHI (e.g., through a workstation, transaction, program, process). | Addressable | AC |
| HIPAA-308-a-4-ii-C | 45 CFR 164.308(a)(4)(ii)(C) | Access establishment and modification | Establish, document, review, and modify a user's right of access based on the access-authorization policy. | Addressable | AC |
| HIPAA-308-a-5-i | 45 CFR 164.308(a)(5)(i) | Security awareness and training (standard) | Implement a security awareness and training program for all workforce members (including management). | Standard | SM |
| HIPAA-308-a-5-ii-A | 45 CFR 164.308(a)(5)(ii)(A) | Security reminders | Periodic security updates/reminders. | Addressable | SM |
| HIPAA-308-a-5-ii-B | 45 CFR 164.308(a)(5)(ii)(B) | Protection from malicious software | Procedures for guarding against, detecting, and reporting malicious software. | Addressable | SM |
| HIPAA-308-a-5-ii-C | 45 CFR 164.308(a)(5)(ii)(C) | Log-in monitoring | Procedures for monitoring log-in attempts and reporting discrepancies. | Addressable | AU |
| HIPAA-308-a-5-ii-D | 45 CFR 164.308(a)(5)(ii)(D) | Password management | Procedures for creating, changing, and safeguarding passwords. | Addressable | IA |
| HIPAA-308-a-6-i | 45 CFR 164.308(a)(6)(i) | Security incident procedures (standard) | Implement policies/procedures to address security incidents. | Standard | SM |
| HIPAA-308-a-6-ii | 45 CFR 164.308(a)(6)(ii) | Response and reporting | Identify and respond to suspected/known incidents; mitigate harmful effects; document incidents and outcomes. | Required | SM |
| HIPAA-308-a-7-i | 45 CFR 164.308(a)(7)(i) | Contingency plan (standard) | Establish (and implement as needed) policies/procedures for responding to an emergency or other occurrence (fire, vandalism, system failure, natural disaster) that damages systems containing ePHI. | Standard | BK |
| HIPAA-308-a-7-ii-A | 45 CFR 164.308(a)(7)(ii)(A) | Data backup plan | Establish/implement procedures to create and maintain retrievable exact copies of ePHI. | Required | BK |
| HIPAA-308-a-7-ii-B | 45 CFR 164.308(a)(7)(ii)(B) | Disaster recovery plan | Establish/implement procedures to restore any loss of data. | Required | BK |
| HIPAA-308-a-7-ii-C | 45 CFR 164.308(a)(7)(ii)(C) | Emergency mode operation plan | Enable continuation of critical business processes for protecting ePHI security while operating in emergency mode. | Required | BK |
| HIPAA-308-a-7-ii-D | 45 CFR 164.308(a)(7)(ii)(D) | Testing and revision procedures | Periodically test and revise contingency plans. | Addressable | BK |
| HIPAA-308-a-7-ii-E | 45 CFR 164.308(a)(7)(ii)(E) | Applications and data criticality analysis | Assess the relative criticality of specific applications and data in support of other contingency plan components. | Addressable | BK |
| HIPAA-308-a-8 | 45 CFR 164.308(a)(8) | Evaluation (standard) | Perform periodic technical and nontechnical evaluation establishing the extent to which security policies/procedures meet the rule's requirements. | Standard | SM |
| HIPAA-308-b-1 | 45 CFR 164.308(b)(1) | Business associate contracts / other arrangements (standard) | Obtain satisfactory assurances (via contract) that a business associate will appropriately safeguard ePHI. | Standard | SM |

#### A.1.3 Physical Safeguards: §164.310 (device/media and workstation subset)

Included where they touch device/media protection and endpoint restriction (per scope). Facility access controls (a) and Workstation use (b) are listed for completeness but are chiefly physical, not cyber.

| control_id | Official citation | Title | Cyber requirement (paraphrase) | R/A | Family |
|---|---|---|---|---|---|
| HIPAA-310-c | 45 CFR 164.310(c) | Workstation security (standard) | Implement physical safeguards for all workstations that access ePHI, to restrict access to authorized users. | Standard | AC |
| HIPAA-310-d-1 | 45 CFR 164.310(d)(1) | Device and media controls (standard) | Govern receipt/removal of hardware and electronic media containing ePHI into/out of a facility and movement within a facility. | Standard | SM |
| HIPAA-310-d-2-i | 45 CFR 164.310(d)(2)(i) | Disposal | Address final disposition of ePHI and/or the hardware/electronic media on which it is stored (media sanitization). | Required | SM |
| HIPAA-310-d-2-ii | 45 CFR 164.310(d)(2)(ii) | Media re-use | Remove ePHI from electronic media before the media are made available for re-use. | Required | SM |
| HIPAA-310-d-2-iii | 45 CFR 164.310(d)(2)(iii) | Accountability | Maintain a record of the movements of hardware/electronic media and any person responsible. | Addressable | AU |
| HIPAA-310-d-2-iv | 45 CFR 164.310(d)(2)(iv) | Data backup and storage | Create a retrievable exact copy of ePHI, when needed, before moving equipment. | Addressable | BK |
| HIPAA-310-a-1 | 45 CFR 164.310(a)(1) | Facility access controls (standard) | Limit physical access to electronic information systems and the facilities housing them while ensuring authorized access. | Standard | AC |
| HIPAA-310-b | 45 CFR 164.310(b) | Workstation use (standard) | Specify the proper functions to be performed and the manner/physical attributes of the surroundings of workstations that access ePHI. | Standard | AC |

---

### A.2 FDA 21 CFR Part 11: Electronic Records; Electronic Signatures

All Part 11 requirements are mandatory when the record/signature falls within Part 11's predicate-rule scope; there is no Required/Addressable split. §11.10 governs *closed* systems; §11.30 adds measures for *open* systems; §§11.50–11.70 govern signature manifestation and linking; §§11.100–11.300 govern electronic signatures and their credential controls.

#### A.2.1 Controls for closed systems: §11.10

| control_id | Official citation | Title | Cyber requirement (paraphrase) | Family |
|---|---|---|---|---|
| PART11-11.10-a | 21 CFR 11.10(a) | Validation | Validate systems to ensure accuracy, reliability, consistent intended performance, and the ability to discern invalid or altered records. | CV |
| PART11-11.10-b | 21 CFR 11.10(b) | Accurate and complete copies | Ability to generate accurate and complete copies of records in both human-readable and electronic form for agency inspection/review/copying. | BK |
| PART11-11.10-c | 21 CFR 11.10(c) | Record protection / retrieval | Protect records to enable accurate and ready retrieval throughout the retention period. | BK |
| PART11-11.10-d | 21 CFR 11.10(d) | Limiting system access | Limit system access to authorized individuals. | AC |
| PART11-11.10-e | 21 CFR 11.10(e) | Audit trails | Use secure, computer-generated, time-stamped audit trails to independently record the date/time of operator entries and actions that create, modify, or delete records; audit trail retained ≥ record retention period and available for review/copying. | AU |
| PART11-11.10-f | 21 CFR 11.10(f) | Operational system checks | Use operational system checks to enforce permitted sequencing of steps and events, as appropriate. | DI |
| PART11-11.10-g | 21 CFR 11.10(g) | Authority checks | Ensure only authorized individuals can use the system, electronically sign a record, access the operation/device, alter a record, or perform the operation at hand. | AC |
| PART11-11.10-h | 21 CFR 11.10(h) | Device checks | Use device (e.g., terminal) checks to determine the validity of the source of data input or operational instruction. | IA |
| PART11-11.10-i | 21 CFR 11.10(i) | Personnel qualifications | Ensure persons who develop, maintain, or use the systems have the education, training, and experience to perform their tasks. | SM |
| PART11-11.10-j | 21 CFR 11.10(j) | Accountability policies | Establish and adhere to written policies holding individuals accountable/responsible for actions initiated under their electronic signatures, to deter record and signature falsification. | DI |
| PART11-11.10-k | 21 CFR 11.10(k) | Controls over systems documentation | Control distribution/access/use of, and revision/change control (with audit trail) over, systems operation and maintenance documentation. | CV |

#### A.2.2 Controls for open systems: §11.30

| control_id | Official citation | Title | Cyber requirement (paraphrase) | Family |
|---|---|---|---|---|
| PART11-11.30 | 21 CFR 11.30 | Controls for open systems | Employ §11.10 controls as applicable *plus* additional measures, such as document encryption and use of appropriate digital signature standards: to ensure record authenticity, integrity, and (as appropriate) confidentiality from creation to receipt. | EN |

#### A.2.3 Electronic signature manifestation and linking: §§11.50, 11.70

| control_id | Official citation | Title | Cyber requirement (paraphrase) | Family |
|---|---|---|---|---|
| PART11-11.50-a | 21 CFR 11.50(a) | Signature manifestations | Signed electronic records must contain the printed name of the signer, the date/time of signing, and the meaning (review, approval, responsibility, authorship) of the signature. | DI |
| PART11-11.50-b | 21 CFR 11.50(b) | Manifestation in human-readable form | The above items are subject to the same controls as electronic records and must appear in any human-readable form (display or printout). | DI |
| PART11-11.70 | 21 CFR 11.70 | Signature/record linking | Electronic and handwritten signatures executed to electronic records must be linked to their records so they cannot be excised, copied, or otherwise transferred to falsify a record by ordinary means. | DI |

#### A.2.4 Electronic signatures: general, components, and credential controls (§§11.100, 11.200, 11.300)

| control_id | Official citation | Title | Cyber requirement (paraphrase) | Family |
|---|---|---|---|---|
| PART11-11.100-a | 21 CFR 11.100(a) | Signature uniqueness | Each electronic signature must be unique to one individual and never reused by or reassigned to anyone else. | IA |
| PART11-11.100-b | 21 CFR 11.100(b) | Identity verification | Verify the identity of an individual before establishing/assigning/certifying/sanctioning that individual's electronic signature. | IA |
| PART11-11.100-c | 21 CFR 11.100(c) | Certification to the agency | Certify to FDA that electronic signatures are intended to be the legally binding equivalent of handwritten signatures. | DI |
| PART11-11.200-a | 21 CFR 11.200(a) | Non-biometric signature components/controls | Employ at least two distinct identification components (e.g., ID code + password); for continuous sessions all components used at first signing then ≥1 component per subsequent signing, otherwise all components each signing; used only by genuine owners; administered so that attempted use by a non-owner requires collaboration of two or more individuals. | IA |
| PART11-11.200-b | 21 CFR 11.200(b) | Biometric signature controls | Biometric-based electronic signatures must be designed to ensure they cannot be used by anyone other than their genuine owners. | IA |
| PART11-11.300-a | 21 CFR 11.300(a) | Credential uniqueness | Maintain the uniqueness of each combined identification code and password so no two individuals share the same combination. | IA |
| PART11-11.300-b | 21 CFR 11.300(b) | Periodic credential revision | Ensure ID code/password issuances are periodically checked, recalled, or revised (e.g., password aging). | IA |
| PART11-11.300-c | 21 CFR 11.300(c) | Loss management | Electronically deauthorize lost/stolen/missing/compromised tokens, cards, or devices and issue replacements under rigorous controls. | IA |
| PART11-11.300-d | 21 CFR 11.300(d) | Transaction safeguards | Prevent unauthorized use of passwords/ID codes and detect and report attempted unauthorized use immediately/urgently to the security unit and, as appropriate, to management. | SM |
| PART11-11.300-e | 21 CFR 11.300(e) | Device testing | Initially and periodically test tokens/cards that bear or generate credential information to confirm they function properly and have not been altered. | IA |

---

### A.3 GxP Data Integrity for Computerised Systems: ALCOA+, EU GMP Annex 11, GAMP 5

#### A.3.1 ALCOA+ data-integrity principles

ALCOA was coined by the U.S. FDA (attributed to Stan Woollen) as a GLP/GMP records-quality standard; the "+" attributes (Complete, Consistent, Enduring, Available) were added by regulators (MHRA/PIC/S/WHO) and are referenced in the FDA 2018 Data Integrity Q&A and MHRA 2018 GXP Data Integrity Guidance. These are *principles* that GxP controls (Annex 11, Part 11) implement, not clauses themselves.

| control_id | Reference | Principle | Cyber requirement (paraphrase) | Family |
|---|---|---|---|---|
| ALCOA-A | MHRA 2018 §; FDA 2018 DI Q&A | Attributable | Data can be attributed to the person/system that generated it (who, when). | DI (+AU) |
| ALCOA-L | MHRA 2018 | Legible | Data are readable and permanent/indelible for the record's life. | DI |
| ALCOA-C | MHRA 2018 | Contemporaneous | Data are recorded at the time of the activity/observation. | AU (+DI) |
| ALCOA-O | MHRA 2018 | Original | The original record (or a validated "true copy") is preserved. | DI |
| ALCOA-Ac | MHRA 2018; FDA 2018 | Accurate | Data are correct, truthful, and error-free (supported by validation, accuracy checks, audit trail). | DI |
| ALCOA-Cp | MHRA 2018 (ALCOA+) | Complete | All data, including repeat/reanalysis and metadata, are retained with no deletions. | DI |
| ALCOA-Cs | MHRA 2018 (ALCOA+) | Consistent | Data follow a consistent, expected sequence (e.g., date/time stamps in order). | DI |
| ALCOA-En | MHRA 2018 (ALCOA+) | Enduring | Data are durable and retained on suitable media throughout the retention period. | BK |
| ALCOA-Av | MHRA 2018 (ALCOA+) | Available | Data are accessible/retrievable for review and audit throughout their lifecycle. | BK |

#### A.3.2 EU GMP Annex 11: Computerised Systems (EudraLex Vol. 4, rev. 1, in force 30 June 2011)

Verified verbatim from the official European Commission PDF. Cyber-relevant clauses (1–17 numbering is the Annex's own). All are "should" expectations that are enforceable under EU GMP.

| control_id | Official citation | Title | Cyber requirement (paraphrase) | Family |
|---|---|---|---|---|
| ANNEX11-1 | Annex 11 cl. 1 | Risk Management | Apply risk management across the system lifecycle (patient safety, data integrity, product quality); base the extent of validation and data-integrity controls on a documented risk assessment. | SM |
| ANNEX11-2 | Annex 11 cl. 2 | Personnel | All personnel have appropriate qualifications, **level of access**, and defined responsibilities. | AC |
| ANNEX11-3 | Annex 11 cl. 3 | Suppliers and Service Providers | Formal agreements with third parties (incl. remote access/maintenance) stating responsibilities; supplier competence/reliability assessed by risk; audit info available to inspectors. | SM |
| ANNEX11-4 | Annex 11 cl. 4 | Validation | Validate the application across relevant lifecycle steps; maintain system inventory and, for critical systems, a system description covering physical/logical arrangements, data flows, interfaces, and **security measures**; verify data are unaltered on migration (cl. 4.8). | CV |
| ANNEX11-5 | Annex 11 cl. 5 | Data | Systems exchanging data electronically must include built-in checks for correct and **secure entry and processing** of data. | DI |
| ANNEX11-6 | Annex 11 cl. 6 | Accuracy Checks | For critical data entered manually, add an accuracy check (second operator or validated electronic means). | DI |
| ANNEX11-7.1 | Annex 11 cl. 7.1 | Data Storage: protection | Secure data by physical and electronic means against damage; check stored data for accessibility, readability, accuracy; ensure access throughout the retention period. | BK |
| ANNEX11-7.2 | Annex 11 cl. 7.2 | Data Storage: backups | Perform regular backups of all relevant data; check integrity, accuracy, and restorability during validation and monitor periodically. | BK |
| ANNEX11-8 | Annex 11 cl. 8 | Printouts | Provide clear printed copies of stored data; for batch-release records, printouts must indicate whether any data changed since original entry. | DI |
| ANNEX11-9 | Annex 11 cl. 9 | Audit Trails | Based on risk, build in a system-generated audit trail of GMP-relevant changes/deletions; document the reason for change/deletion; audit trails available, convertible to intelligible form, and regularly reviewed. | AU |
| ANNEX11-10 | Annex 11 cl. 10 | Change and Configuration Management | Make any change to the system (including configuration) only in a controlled manner per a defined procedure. | CV |
| ANNEX11-11 | Annex 11 cl. 11 | Periodic Evaluation | Periodically evaluate systems to confirm a valid, GMP-compliant state (functionality, deviations, incidents, upgrade history, performance, reliability, **security**, validation status). | CV |
| ANNEX11-12.1 | Annex 11 cl. 12.1 | Security: access restriction | Physical and/or logical controls restrict system access to authorized persons (keys, pass cards, personal codes with passwords, biometrics, restricted access to equipment and data-storage areas). | AC |
| ANNEX11-12.2 | Annex 11 cl. 12.2 | Security: risk-proportionate | The extent of security controls depends on the criticality of the computerised system. | AC |
| ANNEX11-12.3 | Annex 11 cl. 12.3 | Security: authorization records | Record creation, change, and cancellation of access authorizations. | AU |
| ANNEX11-12.4 | Annex 11 cl. 12.4 | Security: operator identity capture | Data/document management systems must record the identity of operators entering, changing, confirming, or deleting data, including date and time. | AU |
| ANNEX11-13 | Annex 11 cl. 13 | Incident Management | Report and assess all incidents (not only system failures/data errors); identify root cause of critical incidents as the basis for CAPA. | SM |
| ANNEX11-14 | Annex 11 cl. 14 | Electronic Signature | Electronic signatures must have the same impact as handwritten signatures within the company, be permanently linked to their record, and include the time and date applied. | DI |
| ANNEX11-15 | Annex 11 cl. 15 | Batch Release | For certification/batch release, permit only Qualified Persons to certify release and clearly identify/record the certifying person, performed via electronic signature. | AC |
| ANNEX11-16 | Annex 11 cl. 16 | Business Continuity | Ensure continuity of support for critical processes during system breakdown (manual/alternative system); arrangements documented and tested. | BK |
| ANNEX11-17 | Annex 11 cl. 17 | Archiving | Archived data checked for accessibility, readability, integrity; ensure and test retrievability if the system changes. | BK |

> Note: A revision of Annex 11 is under EMA consultation (draft published for comment); the version cataloged above is the in-force rev. 1 (2011). Cite the in-force version for compliance claims and note the draft only where forward-looking.

#### A.3.3 ISPE GAMP 5 (2nd Edition, 2022): risk-based validation and AI/ML appendix D11

GAMP 5 is industry guidance (not law) widely accepted by regulators for demonstrating validated GxP computerised systems. It underpins the risk-based validation expected by Annex 11 cl. 1/4 and Part 11 §11.10(a). The 2nd edition (ISPE, published July 2022) incorporates computer software assurance (CSA) thinking and adds Appendix D11 on AI/ML. GAMP 5 is a paywalled ISPE publication; the rows below are paraphrased from ISPE's public description/table of contents and regulator/industry commentary, not from verbatim guide text.

| control_id | Reference | Title | Cyber requirement (paraphrase) | Family |
|---|---|---|---|---|
| GAMP5-RBA | GAMP 5 (2nd ed., 2022), main body | Risk-based, lifecycle validation | Scale validation/assurance effort to system risk, novelty, and complexity; leverage supplier activities; use critical-thinking / CSA to focus testing on high-impact functions and data-integrity-critical requirements. | CV |
| GAMP5-D11 | GAMP 5 (2nd ed., 2022), Appendix D11 | Artificial Intelligence / Machine Learning | Apply a risk-based AI/ML lifecycle (concept → project → operation); distinguish static (fixed post-validation) vs dynamic/adaptive (continuously learning) models; treat training/test data as GxP records under ALCOA+; version and archive each model (architecture, hyperparameters, training dataset); apply access control and segregation of datasets; log development/training/deployment/retraining events with time and user; define performance/acceptance metrics and assess bias; monitor for model drift with thresholds that trigger controlled retraining under change control. | CV (+DI, AU, AC, BK, SM) |

---

## Part B: Normalized Cross-Framework Control Taxonomy

Eight normalized control families with the extracted controls mapped into each. Every extracted control appears in at least one family (primary family = the last column in Part A; families in parentheses in Part A are secondary and also listed here where load-bearing).

| Normalized family | HIPAA (§164.30x) | 21 CFR Part 11 | GxP: Annex 11 / ALCOA+ / GAMP 5 |
|---|---|---|---|
| **AC: Access Control & Authorization** | 312-a-1 (access control), 312-a-2-ii (emergency access), 312-a-2-iii (auto-logoff), 308-a-3 (workforce security A–C), 308-a-4 (info access mgmt A–C), 310-c (workstation security), 310-a-1 (facility access), 310-b (workstation use) | 11.10(d) limiting access, 11.10(g) authority checks | Annex 11 cl. 2 (level of access), 12.1 (access restriction), 12.2 (risk-proportionate), 15 (batch release authority) |
| **IA: Identity & Authentication** | 312-a-2-i (unique user ID), 312-d (person/entity authentication), 308-a-5-ii-D (password mgmt) | 11.10(h) device checks, 11.100(a)(b) signature uniqueness/identity, 11.200(a)(b) signature components, 11.300(a)(b)(c)(e) credential controls | (Annex 11 12.1 authentication methods: keys/passwords/biometrics) |
| **AU: Audit Trail & Logging** | 312-b (audit controls), 308-a-1-ii-D (activity review), 308-a-5-ii-C (log-in monitoring), 310-d-2-iii (accountability) | 11.10(e) secure time-stamped audit trails | Annex 11 cl. 9 (audit trails), 12.3 (authorization records), 12.4 (operator identity/time); ALCOA-A (attributable), ALCOA-C (contemporaneous) |
| **EN: Encryption & Transmission Security** | 312-a-2-iv (encrypt/decrypt at rest), 312-e-1 (transmission security), 312-e-2-i (integrity controls), 312-e-2-ii (encryption in transit) | 11.30 (open systems: encryption + digital signatures) |: |
| **DI: Data Integrity & Non-repudiation (incl. e-signatures)** | 312-c-1 (integrity), 312-c-2 (authenticate ePHI) | 11.10(f) operational checks, 11.10(j) accountability policies, 11.50(a)(b) signature manifestations, 11.70 signature/record linking, 11.100(c) certification | Annex 11 cl. 5 (secure data entry), 6 (accuracy checks), 8 (printouts show change), 14 (electronic signature); ALCOA L/O/Ac/Cp/Cs |
| **BK: Backup, Availability & Contingency** | 308-a-7 (contingency plan A–E), 310-d-2-iv (data backup and storage) | 11.10(b) accurate copies, 11.10(c) record protection/retrieval | Annex 11 cl. 7.1 (secure storage), 7.2 (backups), 16 (business continuity), 17 (archiving); ALCOA-En (enduring), ALCOA-Av (available) |
| **CV: Configuration, Validation & Change Control** | none (308-a-8 evaluation is adjacent; mapped to SM) | 11.10(a) validation, 11.10(k) documentation controls | Annex 11 cl. 4 (validation), 10 (change/config mgmt), 11 (periodic evaluation); GAMP5-RBA (risk-based validation), GAMP5-D11 (AI/ML lifecycle) |
| **SM: Security Management, Risk & Incident Response** | 308-a-1 (security mgmt process A–D), 308-a-2 (assigned responsibility), 308-a-5-i/A/B (awareness, reminders, anti-malware), 308-a-6 (incident procedures), 308-a-8 (evaluation), 308-b-1 (BA contracts), 310-d-1/d-2-i/d-2-ii (device/media controls, disposal, re-use) | 11.10(i) personnel qualifications, 11.300(d) transaction safeguards (detect/report) | Annex 11 cl. 1 (risk mgmt), 3 (suppliers/third parties), 13 (incident mgmt) |

---

## Part C: Mapping of Normalized Families to NIST CSF 2.0 Functions

NIST Cybersecurity Framework 2.0 (released February 2024) organizes outcomes into six Functions: **Govern (GV)**, **Identify (ID)**, **Protect (PR)**, **Detect (DE)**, **Respond (RS)**, **Recover (RC)**. Mapping below shows the primary Function(s) each normalized family serves, with the most relevant CSF 2.0 Categories.

| Normalized family | Primary CSF 2.0 Function(s) | Most relevant CSF 2.0 Categories |
|---|---|---|
| AC: Access Control & Authorization | **Protect** | PR.AA (Identity Management, Authentication & Access Control) |
| IA: Identity & Authentication | **Protect** (policy in **Govern**) | PR.AA (authentication, credential lifecycle); GV.RR (roles/responsibilities) |
| AU: Audit Trail & Logging | **Detect** (supported by **Protect**) | DE.CM (Continuous Monitoring), DE.AE (Adverse Event Analysis); PR.PS logging |
| EN: Encryption & Transmission Security | **Protect** | PR.DS (Data Security: data at rest and in transit) |
| DI: Data Integrity & Non-repudiation | **Protect** (monitoring in **Detect**) | PR.DS (integrity/integrity-checking, e.g., PR.DS-06); DE.CM (integrity monitoring) |
| BK: Backup, Availability & Contingency | **Recover** (resilience design in **Protect**) | RC.RP (Incident Recovery Plan Execution); PR.IR (Technology Infrastructure Resilience), backups under PR.DS |
| CV: Configuration, Validation & Change Control | **Protect** and **Identify** (with **Govern**) | PR.PS (Platform Security: config/change mgmt), PR.IR; ID.AM (Asset Management); ID.RA (Risk Assessment) |
| SM: Security Management, Risk & Incident Response | **Govern**, **Identify**, **Respond** (with **Detect**) | GV.RM (Risk Management Strategy), GV.SC (Cybersecurity Supply Chain Risk Mgmt), GV.RR; ID.RA, ID.IM (Improvement); RS.MA/RS.AN/RS.MI (Incident Management/Analysis/Mitigation), RS.CO |

**Framework-level observation for the paper:** The three biotech frameworks are heavily weighted toward **Protect** (access, encryption, integrity), with strong **Recover** coverage (HIPAA contingency plan; Annex 11 business continuity/backup/archiving) and moderate **Detect/Respond** coverage (HIPAA audit controls + incident procedures; Part 11 audit trails + transaction safeguards; Annex 11 audit trails + incident management). **Govern** is expressed through risk management and supplier/business-associate obligations (HIPAA 308-b, Annex 11 cl. 1/3, GAMP 5 risk-based approach). None of the three prescribes modern network-defense controls (e.g., MFA is only implied by Part 11's two-component signatures and HIPAA "person/entity authentication"; there is no explicit segmentation, EDR, or threat-intel requirement): a gap worth naming in the benchmark.

---

## Part D: Sources

Primary regulatory text (verified verbatim unless noted):

- 45 CFR 164.308: HIPAA Administrative Safeguards (Cornell Law LII mirror of eCFR): https://www.law.cornell.edu/cfr/text/45/164.308
- 45 CFR 164.310: HIPAA Physical Safeguards: https://www.law.cornell.edu/cfr/text/45/164.310
- 45 CFR 164.312: HIPAA Technical Safeguards: https://www.law.cornell.edu/cfr/text/45/164.312
- 45 CFR 164.306: HIPAA Security standards: general rules (Required/Addressable definition): https://www.law.cornell.edu/cfr/text/45/164.306
- Authoritative U.S. source of record for all of the above (was blocking automated fetch during compilation; cite in the paper): eCFR Title 45, Part 164, Subpart C: https://www.ecfr.gov/current/title-45/part-164/subpart-C
- 21 CFR 11.10: Controls for closed systems: https://www.law.cornell.edu/cfr/text/21/11.10
- 21 CFR 11.30: Controls for open systems: https://www.law.cornell.edu/cfr/text/21/11.30
- 21 CFR 11.50: Signature manifestations: https://www.law.cornell.edu/cfr/text/21/11.50
- 21 CFR 11.70: Signature/record linking: https://www.law.cornell.edu/cfr/text/21/11.70
- 21 CFR 11.100: Electronic signatures, general requirements: https://www.law.cornell.edu/cfr/text/21/11.100
- 21 CFR 11.200: Electronic signature components and controls: https://www.law.cornell.edu/cfr/text/21/11.200
- 21 CFR 11.300: Controls for identification codes/passwords: https://www.law.cornell.edu/cfr/text/21/11.300
- eCFR authoritative source for Part 11: https://www.ecfr.gov/current/title-21/chapter-I/subchapter-A/part-11
- EU GMP Annex 11: Computerised Systems (EudraLex Vol. 4, rev. 1, 2011), official European Commission PDF (verified verbatim, all 17 clauses + glossary): https://health.ec.europa.eu/system/files/2016-11/annex11_01-2011_en_0.pdf

Guidance and standards (secondary / paywalled; used for ALCOA+ and GAMP 5; verify verbatim quotations against the originals before publication):

- FDA, "Data Integrity and Compliance With Drug CGMP: Questions and Answers: Guidance for Industry" (Dec 2018): source of ALCOA as FDA data-integrity standard: https://www.fda.gov/regulatory-information/search-fda-guidance-documents/data-integrity-and-compliance-drug-cgmp-questions-and-answers-guidance-industry
- MHRA, "'GXP' Data Integrity Guidance and Definitions" (Rev 1, March 2018): ALCOA+ definitions: https://www.gov.uk/government/publications/guidance-on-gxp-data-integrity
- PIC/S PI 041-1, "Good Practices for Data Management and Integrity in Regulated GMP/GDP Environments" (July 2021): ALCOA+ in inspection context: https://picscheme.org/en/publications
- ISPE GAMP 5: A Risk-Based Approach to Compliant GxP Computerized Systems (2nd Edition, 2022): publication page: https://ispe.org/publications/guidance-documents/gamp-5-guide-2nd-edition
- ISPE GAMP 5 (2nd Edition): Table of Contents (confirms Appendix D11 "Artificial Intelligence and Machine Learning"): https://ispe.org/sites/default/files/publications/guidance-documents/2022-TOC/ISPE-GAMP5-Ed2_TOC.pdf
- ISPE, "New EU AI Regulation and GAMP 5," Pharmaceutical Engineering (Sept/Oct 2023): GAMP 5 / AI context: https://ispe.org/pharmaceutical-engineering/september-october-2023/new-eu-ai-regulation-and-gampr-5
- NIST Cybersecurity Framework (CSF) 2.0, NIST CSWP 29 (Feb 26, 2024): Functions/Categories used in Part C: https://www.nist.gov/cyberframework and https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf

### Verification status / caveats

- **Verified verbatim from primary sources:** all HIPAA §§164.308/.310/.312 rows; all 21 CFR Part 11 rows (§§11.10, 11.30, 11.50, 11.70, 11.100, 11.200, 11.300); all EU GMP Annex 11 rows (clauses 1–17, from the official EC PDF).
- **Verified as to citation but paraphrased (not verbatim), because the source is paywalled/guidance rather than statute:** ISPE GAMP 5 2nd-edition risk-based approach and **Appendix D11** content. The *existence and title* of Appendix D11 and the July 2022 edition date are corroborated by ISPE's own table of contents; the detailed D11 requirement text is synthesized from ISPE/industry commentary and should be confirmed against the purchased guide before quoting in the IEEE paper.
- **ALCOA+ principle definitions** are paraphrased from regulator guidance (FDA 2018, MHRA 2018, PIC/S PI 041); the exact wording of each "+" attribute varies slightly between MHRA, WHO, and PIC/S: cite the specific guidance you rely on.
- **Family assignments are analytical**, not part of the source regulations; several controls legitimately span multiple families (secondary families are shown in parentheses in Part A and cross-listed in Part B).
- The **eCFR** (ecfr.gov) is the U.S. authoritative electronic source; it blocked automated fetching during compilation, so the Cornell LII mirror was used for extraction. Text was consistent with the rule as published; for the paper, cite the eCFR/Federal Register section numbers (they are identical).
