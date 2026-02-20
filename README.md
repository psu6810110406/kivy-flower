# Dream Garden

## สำหรับเพื่อนร่วมทีม (How to Git)

### 1. การดึงโค้ดไปใช้ครั้งแรก (Clone)
```bash
git clone [URL-PROJECT]
git checkout develop

การอัปเดตโค้ด (Pull)
ก่อนเริ่มงานทุกครั้ง ให้ดึงโค้ดล่าสุดจากเพื่อนมาก่อน:

Bash
git pull origin develop
การส่งงาน (Push)
เมื่อแก้ไขเสร็จแล้ว ให้ส่งขึ้นบรานซ์รองดังนี้:

Bash
git add .
git commit -m "อธิบายสั้นๆว่าแก้ข้อไหน"
git push origin develop
Warning: ห้าม Push ขึ้นบรานซ์ main โดยตรง (ถ้าตกลงกันไว้แบบนั้น)


---



### สรุปคำสั่งที่ต้องพิมพ์รัวๆ ตอนนี้:
1. `git init`
2. `git add .`
3. `git commit -m "initial"`
4. `git checkout -b develop`
5. `git remote add origin [URL]`
6. `git push -u origin develop`

**อยากให้ผมช่วยร่างเนื้อหาใน README.md เพิ่มเติมสำหรับโปรเจกต์เฉพาะทาง (เช่น วิธีลง Library หรือรันโปรแกรม) ไหมครับ?**