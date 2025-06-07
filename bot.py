import asyncio
import random
from discord.ext import commands, tasks

# === Konfigurasi ===
DISCORD_USER_TOKEN = "ODkyNDI2OTUyNDA3OTQxMTYw.G1x_IG.VstjYb9giREq4Is6YX99S4oSpMHVOAIFvQGhIw"
CHANNEL_ID = 1377014563878211614
STAGE_CHANNEL_ID = 1377014563878211614

# === Inisialisasi selfbot ===
client = commands.Bot(command_prefix="!", self_bot=True)

pause_until = None
stage_check_pause_until = None  # jeda lokal setelah user lain terdeteksi

emojis = ["supp", "hello", "gm", "yoo", "gn", "hai", "donut", "go", "LFG", "gg donut", "morning", "hello buddy", "go push lv", "try to level up", "donut to the moon", "what??"]


@client.event
async def on_ready():
    print(f"[✅] Login sebagai {client.user}")
    send_and_delete_loop.start()


@client.event
async def on_voice_state_update(member, before, after):
    global pause_until

    if member.id == client.user.id:
        return

    if after.channel and after.channel.id == STAGE_CHANNEL_ID:
        pause_until = asyncio.get_event_loop().time() + 60
        print(f"[⏸️] {member.name} masuk stage — jeda aktif")


@tasks.loop(seconds=5)
async def send_and_delete_loop():
    global pause_until, stage_check_pause_until

    now = asyncio.get_event_loop().time()

    # Tunggu jika sedang masa jeda karena user join stage
    if pause_until and now < pause_until:
        return

    # Tunggu jika masih dalam masa tunda setelah user lain terdeteksi
    if stage_check_pause_until and now < stage_check_pause_until:
        return

    # Cek stage, jika ada user lain, jangan lanjut dan set jeda lokal baru (acak)
    stage_channel = client.get_channel(STAGE_CHANNEL_ID)
    if stage_channel and hasattr(stage_channel, "members"):
        members = [m for m in stage_channel.members if not m.bot]
        if any(m.id != client.user.id for m in members):
            delay = random.uniform(45, 90)
            stage_check_pause_until = now + delay
            print(f"[🚫] Ada user lain di stage, tunggu {int(delay)} detik untuk cek lagi...")
            return
        else:
            stage_check_pause_until = None  # reset jika kosong

    # MODE AKTIF & PASIF
    if not hasattr(send_and_delete_loop, "active_until"):
        send_and_delete_loop.active_until = now + random.uniform(300, 600)
        print("[🟢] Mulai sesi aktif")

    if now > send_and_delete_loop.active_until:
        pause_until = now + random.uniform(60, 150)
        del send_and_delete_loop.active_until
        print("[💤] Masuk mode pasif/AFK")
        return

    if not hasattr(send_and_delete_loop, "next_send_time"):
        send_and_delete_loop.next_send_time = now + random.uniform(60, 120)

    if now < send_and_delete_loop.next_send_time:
        return

    try:
        channel = client.get_channel(CHANNEL_ID)
        if not channel:
            print("[❌] Channel tidak ditemukan.")
            return

        emoji = random.choice(emojis)

        async with channel.typing():
            await asyncio.sleep(random.uniform(0.5, 2.5))

        msg = await channel.send(emoji)
        print(f"[📤] Kirim pesan {emoji}")

        await asyncio.sleep(0.5)
        await msg.delete()
        print("[🗑️] Pesan dihapus")

    except Exception as e:
        print(f"[❌] Error: {e}")

    send_and_delete_loop.next_send_time = now + random.uniform(60, 120)


# Jalankan selfbot
client.run(DISCORD_USER_TOKEN)
