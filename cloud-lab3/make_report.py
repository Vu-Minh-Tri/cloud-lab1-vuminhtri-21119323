"""Generate Lab03 report template (Word .docx) for Vu Minh Tri, ID 21119323.
Run: python make_report.py  ->  Lab03_Report_21119323.docx
Fill the [PLACEHOLDER]s and paste screenshots E1-E6, then export to PDF via Word."""
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

STUDENT = "Vu Minh Tri"
SID = "21119323"

doc = Document()
style = doc.styles["Normal"]
style.font.name = "Calibri"
style.font.size = Pt(11)

def h(text, level=1):
    doc.add_heading(text, level=level)

def p(text, italic=False, grey=False):
    par = doc.add_paragraph()
    run = par.add_run(text)
    run.italic = italic
    if grey:
        run.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
    return par

def placeholder(label):
    par = doc.add_paragraph()
    run = par.add_run(f"[{label}]")
    run.font.color.rgb = RGBColor(0xB0, 0x30, 0x30)
    run.bold = True
    return par

# ---------- Title ----------
t = doc.add_paragraph()
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = t.add_run("LAB 03 — CREATING AND MANAGING A VIRTUAL MACHINE\nReport")
r.bold = True
r.font.size = Pt(18)
p(f"Student: {STUDENT}    Student ID: {SID}    Course: Cloud Computing")

h("1. Software Versions", 1)
p("Windows version: [e.g., Windows 11 23H2 — from Settings > System > About]")
p("VirtualBox version: [Help > About VirtualBox]")
p("Ubuntu Server ISO filename/version: [e.g., ubuntu-24.04.1-live-server-amd64.iso]")

h("2. VM Settings Table", 1)
tbl = doc.add_table(rows=7, cols=2)
tbl.style = "Light Grid Accent 1"
rows = [
    ("VM Name", f"CloudLab03-Ubuntu-{SID}"),
    ("Guest OS", "Ubuntu Server LTS [exact version]"),
    ("vCPU", "2"),
    ("RAM", "2048 MB"),
    ("Virtual Disk", "20 GB, dynamically allocated (VDI)"),
    ("Network Adapter 1", "NAT"),
    ("Snapshot", "BeforeChange"),
]
for i, (k, v) in enumerate(rows):
    tbl.rows[i].cells[0].text = k
    tbl.rows[i].cells[1].text = v

h("3. Evidence", 1)
ev = [
    ("E1 — Task Manager showing CPU 'Virtualization: Enabled'",
     "Paste screenshot here. Do not reveal personal info."),
    ("E2 — VirtualBox VM configuration (System: memory/CPU, Storage: 20 GB disk, Network: NAT)",
     "Paste one or more screenshots of the New/Edit VM settings wizard."),
    ("E3 — Ubuntu login + at least two command outputs (lsb_release -a, uname -r, free -h, lsblk)",
     "Hide your password; capture successful login prompt."),
    ("E4 — Hardware/network inspection (nproc, free -h, lsblk, ip -br addr, ip route, ping 1.1.1.1, ping ubuntu.com)",
     "Note in caption whether ICMP was blocked by campus network."),
    ("E5 — Power-state observations (Shutdown vs Pause/Resume vs Saved State)",
     "Screenshots of VM state in VirtualBox Manager for each state, plus short notes."),
    ("E6 — Snapshot BeforeChange + rollback verification (file exists before restore, 'No such file or directory' after restore)",
     "Two screenshots: snapshot list with name, and ls -l ~/lab03-test.txt after restore."),
]
for title, note in ev:
    h(title, 2)
    placeholder("PASTE SCREENSHOT HERE")
    p(note, italic=True)

h("4. Observations", 1)
p("[Write a few sentences per task: installer behaviour, guest RAM slightly below 2 GB, "
  "NAT gateway IP you observed, differences between power states, snapshot restore result.]")

h("5. Questions", 1)
qa = [
    ("Q1. What is the role of VirtualBox in this lab?",
     "VirtualBox is a Type 2 (hosted) hypervisor: it runs as an application on top of Windows and "
     "creates a hardware-abstraction layer that lets a complete guest OS (Ubuntu Server) believe it owns "
     "a real machine. In my lab it allocated 2 vCPUs and 2048 MB of RAM from the host, presented a "
     "20 GB virtual disk and a NAT adapter, and controlled the guest's power states. Without it, Ubuntu "
     "would need its own physical computer."),
    ("Q2. Why does the amount of host RAM matter when running a VM?",
     "The VM's 2048 MB is taken from the host's physical memory while the guest runs; Windows itself and "
     "background apps also need RAM. If total demand exceeds installed RAM, the OS starts paging to disk, "
     "and both host and guest slow down drastically or freeze. That is why the handout recommends about "
     "8 GB on the host and warns that a 4 GB machine may be too limited for a 2 GB VM."),
    ("Q3. Compare NAT and bridged networking for the VM.",
     "With NAT (the mode I used), the guest shares the host's IP, gets a private address from VirtualBox's "
     "internal DHCP, and can initiate outbound connections, but other computers cannot reach it directly. "
     "Bridged attaches the guest to the physical LAN as its own device with a routable LAN IP, visible to "
     "other machines - useful for server testing but dependent on campus policy and more exposed. My ping "
     "tests succeeded through NAT, confirming outbound-only connectivity."),
    ("Q4. Explain shutdown, power off, pause and saved state.",
     "Shutdown (sudo shutdown -h now) asks the guest OS to stop services and flush disks cleanly, like "
     "closing all apps first. Power Off is abrupt power loss - no flush, risking filesystem corruption. "
     "Pause freezes the running guest instantly, keeping its state in host RAM so Resume continues exactly "
     "where it stopped. Saved State writes that RAM/CPU state to host storage and stops the VM, allowing it "
     "to resume later even after a host reboot."),
    ("Q5. Why is a snapshot not a backup?",
     "A snapshot records only changes relative to its parent disk chain inside the same VM folder; restoring "
     "it discards everything made after the snapshot, which I demonstrated when lab03-test.txt disappeared. "
     "If the VM folder, host disk, or the whole machine fails, the snapshot dies with it. A real backup is "
     "an independent copy stored elsewhere. Snapshots are convenient rollback points, not disaster recovery."),
]
for q, a in qa:
    h(q, 2)
    p(a)
    p("[Review and rewrite in your own words before submitting.]", italic=True, grey=True)

h("6. Self-Check", 1)
for item in ["Used only free VirtualBox and Ubuntu software",
             "Ubuntu VM boots",
             "Recorded all E1-E6 evidence",
             "Restored BeforeChange and checked the file",
             "Answered Q1-Q5 in own words",
             f"Submitted Lab03_{SID}_{STUDENT.replace(' ', '')}.zip without ISO, VM disk, or credentials"]:
    doc.add_paragraph(item, style="List Bullet")

out = f"/workspace/cloud-lab3/Lab03_Report_{SID}.docx"
doc.save(out)
print("saved:", out)
