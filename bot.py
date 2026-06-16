import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
import unicodedata
import io
from datetime import datetime  # ⬅️ DODAJ TO
import re


intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

async def log_to_channel(bot, guild, message: str):
    """Wysyła log do kanału logów bota."""
    try:
        channel = guild.get_channel(BOT_LOG_CHANNEL)
        if channel:
            embed = discord.Embed(
                title="🧾 Log systemowy",
                description=message,
                color=0x5865F2,
                timestamp=datetime.now()
            )
            embed.set_footer(text=f"{bot.user.name} | Log systemu")
            await channel.send(embed=embed)
    except Exception as e:
        print(f"[LOG ERROR] Nie udało się wysłać logu: {e}")


# ===== ROLE SYSTEMOWE =====
PLUS_ROLES = [1104544559733682226, 1104544612347035740, 1104544616826544148, 1351893151731941418, 1351893141589852160]       # ID ról plusów
MINUS_ROLES = [1104544620152623206, 1104544622241390763, 1104544623948480564]      # ID ról minusów
POCHWALA_ROLES = [1362778150249042093, 1362778327332552765, 1362778417380069417]   # ID ról pochwał
WARN_ROLES = [1163083900571103263, 1163084174605959309]       # ID ról warnów
STANOWISKA_ROLES = [1104120114594455626, 1104120114594455627, 1106003624330543234, 1104120114594455629, 1106003848289603636, 1104120114594455630, 1104120114594455631, 1406019662537560247, 1105215277009997917, 1105215433226866782, 1105215434577432576, 1105215416525135943] # ID ról stanowisk

# ===== KANAŁY LOGÓW DLA AWANSÓW I DEGRADÓW =====
AWANS_LOG_CHANNEL = 1441771493527916676   # ID kanału, gdzie lecą awanse
DEGRAD_LOG_CHANNEL = 1441771493527916676  # ID kanału, gdzie lecą degradacje

# ===================== KOMENDA /nadaj =====================
ROLES = {
    "plus": [1104544559733682226, 1104544612347035740, 1104544616826544148, 1351893151731941418, 1351893141589852160],
    "minus": [1104544620152623206, 1104544622241390763, 1104544623948480564],
    "pochwala": [1362778150249042093, 1362778327332552765, 1362778417380069417],
    "warn": [1163083900571103263, 1163084174605959309],
}

EMOTKI = {
    "plus": "✅",
    "minus": "⚠️",
    "pochwala": "🏅",
    "warn": "⛔"
}

CO_COLORS = {
    "plus": 0x2ecc71,
    "minus": 0xe74c3c,
    "pochwala": 0x3498db,
    "warn": 0xf1c40f
}

# Kanały do logowania (Twoje aktualne ID)
CHANNEL_LOGS = {
        "plus": 1441771376263561226,      # plusy i minusy
        "minus": 1441771376263561226,     # plusy i minusy
        "pochwala": 1441771506609684663,  # pochwały
        "warn": 1441771347893162014       # warny
}


# Kanały logów — wpisz własne ID kanałów, gdzie mają iść logi /nadaj
CO_CHANNELS = {
    "plus": 1406767298219606077,
    "minus": 1406767298219606077,
    "pochwala": 1406767298219606077,
    "warn": 1406767298219606077,
}

# Rangi do wypłat (komenda /wyplata)
RANK_PAY = {
    "Mechanik Stażysta": (1_200_000, 40_000),
    "Młodszy Mechanik": (1_400_000, 42_000),
    "Mechanik": (1_600_000, 44_000),
    "Starszy Mechanik": (1_800_000, 46_000),
    "Fachowiec": (2_000_000, 48_000),
    "Majster": (2_200_000, 50_000),
    "Brygadzista": (2_400_000, 52_000),
    "Asystent Zarzadu": (2_000_000, 50_000),
    "Technik": (3_000_000, 50_000),
    "Kierownik": (3_000_000, 50_000),
    "Menadżer": (4_000_000, 50_000),
    "Zastępca Dyrektora": (5_000_000, 50_000),
    "Dyrektor": (6_000_000, 50_000),
    "Zastępca Właściciela": (7_000_000, 50_000),
}
# 🔧 KONFIGURACJA
ROLE_ZARZAD = 1104120114594455633  # ID roli Zarządu

TICKET_KATEGORIE = {
    "tazer": 1395821814214688868,
    "skargi": 1108311357960507393,
    "urlop": 1335665214758060123,
    "zarzad": 1335666453453471866,
    "konkurs": 1335667023681814588,
    "wyplaty": 1335667043508289576,
    "aktywnosc": 1413612149963624568,
    "ranga": 1439028831142023229,
}

TRANSCRIPTY = {
    "tazer": 1395822355011604600,
    "skargi": 1395822381049581581,
    "urlop": 1395823120765681674,
    "zarzad": 1395822400309821662,
    "konkurs": 1395822435915534498,
    "wyplaty": 1395822464352780311,
    "aktywnosc": 1433530823784792145,
}

# ===== FORMULARZE DO TICKETÓW =====
FORMULARZE = {
    "urlop": (
        "```URLOP\n"
        "Imię i Nazwisko IC:\n"
        "Do kiedy:\n"
        "Powód IC:\n"
        "Powód OOC:```\n"
    ),
    "aktywnosc": (
        "```ZMNIEJSZONA AKTYWNOŚĆ\n"
        "Imię i Nazwisko IC:\n"
        "Do kiedy:\n"
        "Powód:```\n"
    ),
    "tazer": (
        "```TAZER / KAJDANKI\n"
        "Imię i Nazwisko IC:\n"
        "SSN:\n"
        "Co chcesz otrzymać: Tazer / Kajdanki / Oba```\n"
    ),
    "wyplaty": (
        "```WYPŁATY\n"
        "Imię i Nazwisko IC:\n"
        "Ilość godzin:\n"
        "Numer telefonu IC:```\n"
    ),
    "skargi": (
        "```SKARGA\n"
        "Na kogo składasz skargę:\n"
        "Powód skargi:\n"
        "Dowody (np. screeny, nagrania):```\n"
    ),
    "zarzad": (
        "```SPRAWA DO ZARZĄDU\n"
        "Imię i Nazwisko IC:\n"
        "Temat sprawy:\n"
        "Opis sytuacji:```\n"
    ),
    "konkurs": (
        "```KONKURS\n"
        "Imię i Nazwisko IC:\n"
        "Nazwa konkursu:\n"
        "Jaka była nagroda:```\n"
    ),
     "ranga": (
        "```ZAMROŻENIE RANGI\n"
        "Imię i Nazwisko IC:\n"
        "Czas zamrożenia rangi:\n"
        "Powód:```\n"
     ),    
}

# Id kategorii logow
BOT_LOG_CHANNEL = 1406767298219606077  # <--- tu wpisz ID kanału logów bota


# ===== FUNKCJA CZYSZCZĄCA NAZWĘ =====
def czysta_nazwa(nazwa: str) -> str:
    # Zamień polskie znaki na zwykłe
    nazwa = unicodedata.normalize("NFKD", nazwa).encode("ascii", "ignore").decode("ascii")
    # Zamień spacje i dziwne znaki na myślniki
    nazwa = re.sub(r"[^a-zA-Z0-9\-]", "-", nazwa)
    nazwa = nazwa.lower().strip("-")
    # Jeśli po czyszczeniu jest pusto, daj ID użytkownika
    if not nazwa:
        nazwa = "user"
    return nazwa[:90]  # Discord limit: max 100 znaków



@bot.tree.command(name="embed", description="Tworzy zaawansowany embed z opcjonalnym obrazkiem.")
@app_commands.describe(
    tytul="Tytuł embedu",
    opis="Opis (możesz używać pogrubienia **tak**, kursywy *tak* i nowej linii \\n)",
    kolor="Kolor w HEX, np. #3498db",
    obraz_url="Link do obrazu (opcjonalnie)"
)

# ===== KOMENDA /embed =====
@app_commands.checks.has_permissions(administrator=True)
async def embed(
    interaction: discord.Interaction,
    tytul: str,
    opis: str,
    kolor: str = "#2ecc71",
    obraz_url: str = None
):
    try:
        # --- Zamiana \n na prawdziwe entery ---
        opis = opis.replace("\\n", "\n")  # 👈 TO DODAJ TUTAJ

        # --- Konwersja koloru ---
        kolor = int(kolor.replace("#", ""), 16)

        # --- Tworzenie embedu ---
        embed = discord.Embed(
            title=tytul,
            description=opis,
            color=kolor,
            timestamp=datetime.now()
        )

        # --- Ustaw obraz, jeśli podano ---
        if obraz_url:
            embed.set_image(url=obraz_url)

        embed.set_footer(
            text=f"Wysłane przez {interaction.user.display_name}",
            icon_url=interaction.user.display_avatar.url
        )

        # --- Wysłanie embedu ---
        await interaction.channel.send(embed=embed)
        await interaction.response.send_message("✅ Embed wysłany pomyślnie!", ephemeral=True)

        print(f"[EMBED] {interaction.user} wysłał embed: '{tytul}'")

    except ValueError:
        await interaction.response.send_message("❌ Nieprawidłowy kolor! Użyj np. `#1abc9c`.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message("❌ Wystąpił błąd przy tworzeniu embedu.", ephemeral=True)
        print(f"[BŁĄD] /embed: {type(e).__name__} — {e}")

@bot.tree.command(name="edytuj-embed", description="Podmień zdjęcie w istniejącym embedzie.")
@app_commands.describe(
    message_id="ID wiadomości z embedem do edycji",
    obraz_url="Nowy link do obrazu"
)
@app_commands.checks.has_permissions(administrator=True)
async def edytuj_embed(
    interaction: discord.Interaction,
    message_id: str,
    obraz_url: str
):
    try:
        # --- Pobranie wiadomości ---
        try:
            msg_id = int(message_id)
        except ValueError:
            await interaction.response.send_message("❌ Podaj poprawne ID wiadomości (same cyfry).", ephemeral=True)
            return

        message = await interaction.channel.fetch_message(msg_id)
        if not message or not message.embeds:
            await interaction.response.send_message("⚠️ Nie znaleziono embedu w tej wiadomości!", ephemeral=True)
            return

        # --- Pobranie istniejącego embedu ---
        old_embed = message.embeds[0]

        # --- Utworzenie kopii embedu z nowym obrazem ---
        new_embed = discord.Embed.from_dict(old_embed.to_dict())
        new_embed.set_image(url=obraz_url)
        new_embed.set_footer(
            text=f"Zaktualizowane przez {interaction.user.display_name}",
            icon_url=interaction.user.display_avatar.url
        )

        # --- Edycja wiadomości ---
        await message.edit(embed=new_embed)
        await interaction.response.send_message(f"✅ Zdjęcie w embeddzie `{message_id}` zostało zaktualizowane!", ephemeral=True)

        print(f"[EMBED] {interaction.user} zaktualizował obraz w wiadomości {message_id}")

    except discord.NotFound:
        await interaction.response.send_message("❌ Nie znaleziono wiadomości o podanym ID.", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("❌ Brak uprawnień do edycji tej wiadomości.", ephemeral=True)
    except Exception as e:
        print(f"[BŁĄD] /edytuj-embed: {type(e).__name__} — {e}")
        await interaction.response.send_message("❌ Wystąpił błąd podczas edycji embedu.", ephemeral=True)

# ===== KOMENDA /nadaj =====
@bot.tree.command(name="nadaj", description="Nadaj plus, minus, pochwałę, warn, awans lub degrad (wielu osobom naraz).")
@app_commands.describe(co="Typ (plus, minus, pochwala, warn, awans, degrad)", komu="Użytkownicy (można wielu, oddziel spacją)", powod="Powód nadania")
async def nadaj(interaction: discord.Interaction, co: str, komu: str, powod: str):
    co = co.lower()
    dozwolone_typy = list(ROLES.keys()) + ["awans", "degrad"]

    if co not in dozwolone_typy:
        await interaction.response.send_message(
            f"⚠️ Nieprawidłowy typ: `{co}`.\nDostępne: {', '.join(dozwolone_typy)}.",
            ephemeral=True
        )
        return

    # --- Rozpoznanie wielu użytkowników ---
    mentions = komu.split()
    targets = []
    for m in mentions:
        try:
            user_id = int(m.strip("<@!>"))
            member = interaction.guild.get_member(user_id)
            if member:
                targets.append(member)
        except Exception:
            continue

    if not targets:
        await interaction.response.send_message("❌ Nie znaleziono żadnych poprawnych użytkowników.", ephemeral=True)
        return

    # --- Akcja dla plus, minus, pochwała, warn ---
    if co not in ["awans", "degrad"]:
        nadani = []
        for member in targets:
            guild_roles = [interaction.guild.get_role(rid) for rid in ROLES[co]]
            user_roles_ids = {role.id for role in member.roles}
            next_role = None
            for role in guild_roles:
                if role.id not in user_roles_ids:
                    next_role = role
                    break
            if not next_role:
                continue
            if interaction.guild.me.top_role.position <= next_role.position:
                continue
            await member.add_roles(next_role, reason=f"Nadane przez {interaction.user} ({powod})")
            nadani.append((member, next_role))

        if not nadani:
            await interaction.response.send_message(
                "⚠️ Żadnemu użytkownikowi nie nadano nowej rangi (mogli już ją mieć).",
                ephemeral=True
            )
            return

        # --- Tworzenie i wysyłka embeda ---
        embed = discord.Embed(
            title=f"{EMOTKI.get(co, '🎯')} Nadano {co.capitalize()}",
            color=CO_COLORS.get(co, 0x2f3136),
            timestamp=datetime.now()
        )
        opis_lista = "\n".join([f"👤 {m.mention} — {r.mention}" for m, r in nadani])
        embed.add_field(name="Użytkownicy i nadane role", value=opis_lista, inline=False)
        embed.add_field(name="🧑‍⚖️ Nadający", value=interaction.user.mention, inline=True)
        embed.add_field(name="📄 Powód", value=powod, inline=False)
        embed.set_footer(text="Los Santos Customs | System Ról",
                         icon_url=interaction.guild.icon.url if interaction.guild.icon else None)

        channel_id = CHANNEL_LOGS.get(co)
        if channel_id:
            log_channel = interaction.guild.get_channel(channel_id)
            if log_channel:
                pingi = " ".join([m.mention for m, _ in nadani])
                await log_channel.send(content=pingi, embed=embed)

        await interaction.response.send_message("✅ Role zostały pomyślnie nadane!", ephemeral=True)
        return

    # --- Akcja dla awans / degrad ---
    if co in ["awans", "degrad"]:
        for member in targets:
            # ❌ Usuwamy tylko role "minus" (plusy zostają!)
            for rid in ROLES.get("minus", []):
                r = interaction.guild.get_role(rid)
                if r and r in member.roles:
                    await member.remove_roles(r, reason="Awans/Degrad — reset ocen ujemnych")

            # 🔍 Znajdź aktualną rolę stanowiska
            current_index = None
            member_role_ids = [r.id for r in member.roles]
            for i, role_id in enumerate(STANOWISKA_ROLES):
                if role_id in member_role_ids:
                    current_index = i
                    break

            if current_index is None:
                await interaction.channel.send(
                    f"⚠️ {member.mention} nie ma żadnej roli stanowiska, więc nie mogę wykonać {'awansu' if co == 'awans' else 'degradu'}."
                )
                continue

            # ➕ Wyznacz nowy indeks
            if co == "awans":
                new_index = current_index + 1 if current_index + 1 < len(STANOWISKA_ROLES) else None
            else:
                new_index = current_index - 1 if current_index - 1 >= 0 else None

            if new_index is None:
                await interaction.channel.send(
                    f"⚠️ {member.mention} nie może już zostać {'awansowany' if co == 'awans' else ' zdegradowany'} dalej."
                )
                continue

            old_role = interaction.guild.get_role(STANOWISKA_ROLES[current_index])
            new_role = interaction.guild.get_role(STANOWISKA_ROLES[new_index])

            await member.remove_roles(old_role, reason=f"{co.capitalize()} — {powod}")
            await member.add_roles(new_role, reason=f"{co.capitalize()} — {powod}")

            # 🧾 Embed logu
            embed = discord.Embed(
                title=f"{'⬆️ Awans' if co == 'awans' else '⬇️ Degrad'} użytkownika",
                color=0x2ecc71 if co == "awans" else 0xe67e22,
                timestamp=datetime.now()
            )
            embed.add_field(name="👤 Pracownik", value=member.mention, inline=True)
            embed.add_field(name="🧑‍🏭 Wykonał", value=interaction.user.mention, inline=True)
            embed.add_field(name="📄 Powód", value=powod, inline=False)
            embed.add_field(name="🏷️ Zmiana stanowiska", value=f"Z {old_role.mention} ➜ {new_role.mention}", inline=False)
            embed.set_footer(
                text=f"Los Santos Customs | {'Awans' if co == 'awans' else 'Degrad'}",
                icon_url=interaction.guild.icon.url if interaction.guild.icon else None
            )

            log_channel = interaction.guild.get_channel(
                AWANS_LOG_CHANNEL if co == "awans" else DEGRAD_LOG_CHANNEL
            )
            if log_channel:
                await log_channel.send(content=member.mention, embed=embed)
                print(f"[INFO] {co.capitalize()} wykonany: {member} ({old_role.name} → {new_role.name}) i wysłany do logów.")

        # ✅ Odpowiedź do użytkownika — po zakończeniu pętli
        await interaction.response.send_message(
            f"✅ Wykonano {'awans' if co == 'awans' else 'degrad'} dla wskazanych osób.",
            ephemeral=True
        )

# ===== KOMENDA /wyplata =====
@bot.tree.command(name="wyplata", description="Oblicz wypłatę na podstawie rangi i godzin")
@app_commands.describe(ranga="Wybierz rolę (np. @Dyrektor)", godziny="Ilość godzin pracy")
async def wyplata(interaction: discord.Interaction, ranga: discord.Role, godziny: float):
    # Sprawdzenie, czy rola istnieje w słowniku wypłat
    if ranga.name not in RANK_PAY:
        await interaction.response.send_message(
            f"Nieznana ranga: **{ranga.name}**.", ephemeral=True
        )
        return

    norma, za_godzine = RANK_PAY[ranga.name]

    if godziny < 10:
        await interaction.response.send_message(
            "Liczba godzin powinna być co najmniej 10 (norma).", ephemeral=True
        )
        return

    dodatkowe_godziny = godziny - 10
    wyplata_kwota = norma + dodatkowe_godziny * za_godzine

    # Formatowanie liczb
    wyplata_fmt = f"{wyplata_kwota:,.0f} $"

    # Wiadomość w ładnym formacie
    msg = (
        f"💰 Rola: {ranga.mention}\n"
        f"⏱️ Godziny: {godziny}\n"
        f"📊 Wypłata: {wyplata_fmt}"
    )

    await interaction.response.send_message(msg)

@bot.tree.command(name="utworz", description="Utwórz kanały z formularzem dla użytkownika")
@app_commands.describe(uzytkownik="Osoba, dla której mają zostać utworzone kanały")
async def utworz(interaction: discord.Interaction, uzytkownik: discord.Member):
    await interaction.response.defer(ephemeral=True, thinking=True)

    # ✅ TYLKO TA KATEGORIA
    KATEGORIE = [1132010186396155914]
    stworzono_kanaly = []

    for kat_id in KATEGORIE:
        kategoria = interaction.guild.get_channel(kat_id)
        if not isinstance(kategoria, discord.CategoryChannel):
            await interaction.followup.send(
                f"❌ Nie znaleziono kategorii `{kat_id}`.",
                ephemeral=True
            )
            return

        nazwa_kanalu = czysta_nazwa(uzytkownik.display_name)[:90]
        print(f"[DEBUG] Tworzę kanał: {nazwa_kanalu} w kategorii {kategoria.name}")

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            uzytkownik: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }

        try:
            kanal = await kategoria.create_text_channel(
                name=nazwa_kanalu,
                overwrites=overwrites
            )
            stworzono_kanaly.append(kanal)
        except discord.HTTPException as e:
            await interaction.followup.send(
                f"❌ Błąd przy tworzeniu kanału `{nazwa_kanalu}`: {e}",
                ephemeral=True
            )
            continue

        WIADOMOSC = (
            f"{uzytkownik.mention}\n"
            "```Co było robione:\n"
            "Cena:\n"
            "Model Auta:\n"
            "Zdjęcie Dowodu:\n"
            "Tablica rejestracyjna pojazdu:```"
        )

        try:
            await kanal.send(WIADOMOSC)
        except discord.HTTPException as e:
            print(f"[DEBUG] Nie udało się wysłać wiadomości w kanale {nazwa_kanalu}: {e}")

    if stworzono_kanaly:
        kanaly_txt = "\n".join([k.mention for k in stworzono_kanaly])
        await interaction.followup.send(
            f"✅ Utworzono kanał dla {uzytkownik.mention}:\n{kanaly_txt}",
            ephemeral=True
        )

        await log_to_channel(
            bot,
            interaction.guild,
            f"📂 {interaction.user.mention} utworzył kanał dla {uzytkownik.mention}: {kanaly_txt}"
        )
    else:
        await interaction.followup.send(
            f"⚠️ Nie udało się utworzyć kanału dla {uzytkownik.mention}.",
            ephemeral=True
        )



# ===== KOMENDA /oblicz =====
@bot.tree.command(name="oblicz", description="Oblicz kwotę po odjęciu procentu od sumy")
@app_commands.describe(procent="Procent do odjęcia (np. 25%)", suma="Całkowita kwota (np. 6000000)")
async def oblicz(interaction: discord.Interaction, procent: str, suma: float):
    try:
        # Usunięcie znaku % jeśli użytkownik go wpisał
        if procent.endswith("%"):
            procent = procent[:-1]

        procent_val = float(procent)

        # Obliczanie kwoty po odjęciu procentu
        wynik = suma * (1 - (procent_val / 100))

        # Formatowanie liczb z przecinkami i dwoma miejscami po przecinku
        suma_fmt = f"{suma:,.0f} $".replace(",", " ")
        procent_fmt = f"{procent_val}%"
        wynik_fmt = f"{wynik:,.0f} $".replace(",", " ")

        # Wiadomość dla użytkownika
        msg = (
            f" **Kwota:** {suma_fmt}\n"
            f" **Procent:** {procent_fmt}\n"
            f" **Suma:** {wynik_fmt}"
        )

        await interaction.response.send_message(msg)

    except Exception as e:
        await interaction.response.send_message(f"❌ Błąd: {e}", ephemeral=True)


    # ===== KOMENDA /clear =====
@bot.tree.command(name="clear", description="Wyczyść wiadomości z kanału")
@app_commands.describe(ilosc="Ilość wiadomości do usunięcia (max 1000)")
async def clear(interaction: discord.Interaction, ilosc: int):
    # Sprawdzenie uprawnień
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("🚫 Nie masz uprawnień do czyszczenia wiadomości.", ephemeral=True)
        return

    # Ograniczenie ilości
    if ilosc < 1 or ilosc > 1000:
        await interaction.response.send_message("⚠️ Podaj liczbę od 1 do 1000.", ephemeral=True)
        return

    # Usuwanie wiadomości
    await interaction.channel.purge(limit=ilosc)
    await interaction.response.send_message(
        f"🧹 Usunięto **{ilosc}** wiadomości z kanału {interaction.channel.mention}.",
        ephemeral=True
    )

@bot.event
async def on_member_join(member: discord.Member):
    print(f"🚪 {member} ({member.id}) dołączył do {member.guild.name}")

    # === 1️⃣ Wiadomość prywatna ===
    try:
        powitanie_pv = (
            f"👋 **Witaj na serwerze Los Santos Customs, {member.name}!**\n\n"
            f"🚗 Aby rozpocząć pracę, ustaw swój **nick IC** w formacie:\n"
            f"👉 `Imię Nazwisko`\n\n"
            f"Przykład: `John Smith`\n\n"
            f"Po ustawieniu nicku możesz skontaktować się z zarządem, aby odebrać joba.\n"
            f"Miłej gry i powodzenia w pracy! 💪"
        )
        await member.send(powitanie_pv)
        print(f"✅ Wysłano prywatne powitanie do {member.name}.")
    except discord.Forbidden:
        print(f"⚠️ Nie można wysłać DM do {member.name} — ma wyłączone wiadomości prywatne.")
    except Exception as e:
        print(f"❌ Błąd podczas wysyłania DM do {member.name}: {e}")

@bot.event
async def on_member_join(member: discord.Member):
    print(f"🚪 {member} ({member.id}) dołączył do {member.guild.name}")

    # === 1️⃣ Wiadomość prywatna ===
    try:
        powitanie_pv = (
            f"👋 **Witaj na serwerze Los Santos Customs, {member.name}!**\n\n"
            f"🚗 Aby rozpocząć pracę, ustaw swój **nick IC** w formacie:\n"
            f"👉 `Imię Nazwisko`\n\n"
            f"Przykład: `John Smith`\n\n"
            f"Po ustawieniu nicku możesz skontaktować się z zarządem, aby odebrać joba.\n"
            f"Miłej gry i powodzenia w pracy! 💪"
        )
        await member.send(powitanie_pv)
        print(f"✅ Wysłano prywatne powitanie do {member.name}.")
    except discord.Forbidden:
        print(f"⚠️ Nie można wysłać DM do {member.name} — ma wyłączone wiadomości prywatne.")
    except Exception as e:
        print(f"❌ Błąd podczas wysyłania DM do {member.name}: {e}")

    # === 2️⃣ Wiadomość powitalna na kanale ===
    kanal_powitania_id = 1442845577862971423  # 🔧 podaj właściwe ID kanału
    kanal_powitania = member.guild.get_channel(kanal_powitania_id)

    if not kanal_powitania:
        print(f"⚠️ Kanał powitań o ID {kanal_powitania_id} nie został znaleziony!")
        return

    powitania = [
        f"🙋 **Nowy mechanik dołączył do warsztatu!**\nWitaj {member.mention}!",
    ]

    import random
    tekst = random.choice(powitania)

    embed = discord.Embed(
        title="🛠️ Witaj w Los Santos Customs!",
        description=tekst,
        color=0x2ecc71
    )

    if member.display_avatar:
        embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text="Zespół LSC | Witamy na serwerze")

    try:
        await kanal_powitania.send(embed=embed)
        print(f"✅ Powitano {member.name} na kanale {kanal_powitania.name}")
    except discord.Forbidden:
        print("❌ Bot nie ma uprawnień do wysyłania wiadomości na kanale powitań!")
    except Exception as e:
        print(f"❌ Błąd przy wysyłaniu wiadomości powitalnej: {e}")

class CloseTicketButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Zamknij Ticket",
            style=discord.ButtonStyle.danger,
            emoji="🔒",
            custom_id="close_ticket_button"
        )

    async def callback(self, interaction: discord.Interaction):
        channel = interaction.channel
        member = interaction.user

        await interaction.response.defer(ephemeral=True)

        try:
            # Generowanie transcriptu
            messages = [
                f"[{msg.created_at:%Y-%m-%d %H:%M}] {msg.author}: {msg.content}"
                async for msg in channel.history(limit=None, oldest_first=True)
            ]
            transcript_text = "\n".join(messages) or "Brak wiadomości w tickecie."
            transcript_file = discord.File(
                io.BytesIO(transcript_text.encode("utf-8")),
                filename=f"transcript_{channel.name}.txt"
            )

            # Kanał docelowy transcriptu
            ticket_type = next(
                (typ for typ, cat_id in TICKET_KATEGORIE.items()
                 if str(cat_id) == str(channel.category.id)),
                None
            )
            target_channel_id = TRANSCRIPTY.get(ticket_type)
            target_channel = interaction.guild.get_channel(target_channel_id) if target_channel_id else None

            if target_channel:
                await target_channel.send(
                    content=f"📝 Transcript z **{channel.name}** (zamknięty przez {member.mention})",
                    file=transcript_file
                )

            # Komunikat i zamknięcie kanału
            await interaction.followup.send("✅ Ticket zostanie zamknięty za 5 sekund...", ephemeral=True)
            await asyncio.sleep(5)
            await channel.delete(reason=f"Ticket zamknięty przez {member}")
            print(f"[TICKET] Ticket {channel.name} zamknięty przez {member}")

        except Exception as e:
            print(f"[BŁĄD] Nie udało się zamknąć ticketa: {e}")
            await interaction.followup.send("❌ Wystąpił błąd podczas zamykania ticketa.", ephemeral=True)


# ===== CLOSE BUTTON / VIEW =====
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CloseTicketButton())

# ===== MENU WYBORU TYPÓW TICKETÓW =====
class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="🔫 Tazer-Kajdanki", value="tazer", description="Odbierz sprzęt."),
            discord.SelectOption(label="⚖️ Skargi", value="skargi", description="Zgłoś skargę na pracownika."),
            discord.SelectOption(label="🏖️ Urlop", value="urlop", description="Wniosek o urlop."),
            discord.SelectOption(label="🧰 Sprawa do Zarządu", value="zarzad", description="Kontakt z zarządem."),
            discord.SelectOption(label="🏆 Konkurs", value="konkurs", description="Weź udział w konkursie."),
            discord.SelectOption(label="💰 Wypłaty", value="wyplaty", description="Odbierz zaległą wypłatę."),
            discord.SelectOption(label="😴 Zmniejszona aktywność", value="aktywnosc", description="Zgłoś niską aktywność."),
            discord.SelectOption(label="🧊 Zamrożona ranga", value="ranga", description="Zamroż swoją rangę"),
        ]
        super().__init__(
            placeholder="🎟️ Wybierz typ ticketa...",
            options=options,
            custom_id="ticket_select_menu"
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)

        typ = self.values[0]
        user = interaction.user
        print(f"[TICKET] {user} tworzy ticket typu '{typ}'.")

        try:
            category_id = TICKET_KATEGORIE.get(typ)
            category = interaction.guild.get_channel(category_id)

            if not category or not isinstance(category, discord.CategoryChannel):
                await interaction.followup.send("⚠️ Nie znaleziono kategorii dla tego typu ticketa.", ephemeral=True)
                return

            zarzad_role = interaction.guild.get_role(ROLE_ZARZAD)
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                user: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, embed_links=True),
                interaction.guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True),
            }
            if zarzad_role:
                overwrites[zarzad_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

            base_name = f"{typ}-{user.display_name}".lower()
            nazwa = "".join(c for c in base_name if c.isalnum() or c in "-_")[:90]
            if not nazwa:
                nazwa = f"{typ}-{user.id}"

            ticket_channel = await interaction.guild.create_text_channel(
                name=nazwa,
                category=category,
                overwrites=overwrites,
                reason=f"Nowy ticket typu {typ} od {user}"
            )

            # Jeden, poprawny embed
            embed = discord.Embed(
                title=f"🎫 Ticket — {typ.capitalize()}",
                description=f"{user.mention}, Twój ticket został utworzony!\nWypełnij formularz poniżej.",
                color=0x00bfa5,
                timestamp=datetime.now()
            )
            embed.set_footer(text="Los Santos Customs | System Ticketów")
            

            # Wyślij embed, formularz i view tylko RAZ każdy (do ticket_channel)
            await ticket_channel.send(embed=embed)
            
            formularz = FORMULARZE.get(typ, "Brak formularza.")
            await ticket_channel.send(f"📋 **Wypełnij wzór:**\n{formularz}")
            
            view = CloseTicketView()
            await ticket_channel.send(view=view)

            # Potwierdzenie dla użytkownika, że ticket został utworzony
            await interaction.followup.send(f"✅ Ticket utworzony: {ticket_channel.mention}", ephemeral=True)

        except Exception as e:
            # Logujemy szczegóły błędu do konsoli — ważne do debugowania
            print(f"[BŁĄD] {type(e).__name__}: {e}")
            # Możesz rozwinąć log, np. traceback.print_exc()
            await interaction.followup.send("❌ Wystąpił błąd podczas tworzenia ticketa.", ephemeral=True)


# ===== PERSISTENT VIEW =====
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())


# ===== KOMENDA /ticket-setup =====
@bot.tree.command(name="ticket-setup", description="Wyświetla panel ticketów w tym kanale")
async def ticket_setup(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎟️ System Ticketów — Los Santos Customs",
        description=(
            "Wybierz z menu poniżej kategorię, aby utworzyć nowy ticket:\n\n"
            "🔫 **Tazer-Kajdanki** — Odbiór sprzętu\n"
            "⚖️ **Skargi** — Zgłoś problem lub skargę\n"
            "🏖️ **Urlop** — Wniosek o urlop\n"
            "🧰 **Zarząd** — Kontakt z zarządem\n"
            "🏆 **Konkurs** — Udział w konkursie\n"
            "💰 **Wypłaty** — Odbierz zaległą wypłatę\n"
            "😴 **Zmniejszona aktywność** — Zgłoś niską aktywność\n"
            "🧊 **Zamrożenie rangi** — Zamróź swoją rangę"
        ),
        color=0x00bfa5,
        timestamp=datetime.now()
    )
    embed.set_footer(
        text="Los Santos Customs | System Ticketów",
        icon_url=interaction.guild.icon.url if interaction.guild.icon else None
    )

    await interaction.response.send_message(embed=embed, view=TicketView())
    print(f"[TICKET] {interaction.user} użył komendy /ticket-setup w kanale {interaction.channel.name}.")


@bot.event
async def on_member_remove(member):
    """Loguje, gdy ktoś opuści serwer"""
    await log_to_channel(bot, member.guild, f"🚪 Użytkownik **{member}** opuścił serwer.")

@bot.event
async def on_app_command_completion(interaction: discord.Interaction, command: discord.app_commands.Command):
    """Loguje każde użycie komendy slash"""
    guild = interaction.guild
    user = interaction.user
    channel = interaction.channel

    msg = (
        f"**Komenda:** /{command.name}\n"
        f"**Użył:** {user.mention} ({user.id})\n"
        f"**Kanał:** {channel.mention if channel else 'DM'}\n"
        f"**Czas:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    await log_to_channel(bot, guild, msg)
@bot.event
async def on_ready():
    print("======================================")
    print(f"🚀 Zalogowano jako: {bot.user} (ID: {bot.user.id})")
    print(f"🌐 Serwery: {[g.name for g in bot.guilds]}")
    print("======================================")

    try:
        synced = await bot.tree.sync()
        print(f"✅ Slash commands zsynchronizowane ({len(synced)}).")
    except Exception as e:
        print(f"❌ Błąd synchronizacji komend: {e}")

    # === BARDZO WAŻNE: Persistent Views ===
    try:
        bot.add_view(TicketView())        # Select menu działa po restarcie
        bot.add_view(CloseTicketView())   # Przycisk zamykania działa po restarcie ✅
        print("🎟️ Wszystkie persistent View zostały zarejestrowane ✅")
    except Exception as e:
        print(f"⚠️ Błąd persistent View: {e}")

    print("✅ Bot jest gotowy do działania!")
# ===== START BOTA =====
if __name__ == "__main__":
    try:
        bot.run("MTQ2NTAzNzg0MDAxMzMzMjcyMw.Grhzws.e_z8Am192C_c7B2uKZ8tfFNy4_x4MWZ4pW1kV4")
    except Exception as e:
        print(f"❌ Błąd podczas uruchamiania bota: {e}")
