#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate professional 8-frame spritesheets for Location 3 Bosses in survivors:
1. boss_cyber_cerberus_walk.webp & boss_cyber_cerberus_attack.webp & boss_cyber_cerberus_sheet.webp
2. boss_bio_butcher_walk.webp & boss_bio_butcher_attack.webp & boss_bio_butcher_sheet.webp
3. boss_neuro_overmind_float.webp & boss_neuro_overmind_attack.webp & boss_neuro_overmind_sheet.webp
"""

import os
import sys
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

MONSTERS_DIR = r"C:\Users\alexg\Desktop\survivors\img\monsters"

def ensure_rgba(img):
    return img.convert("RGBA")

# ==============================================================================
# 1. CYBER-CERBERUS (Кибер-Цербер)
# ==============================================================================
def generate_cyber_cerberus_sheets():
    src_path = os.path.join(MONSTERS_DIR, "boss_cyber_cerberus.webp")
    if not os.path.exists(src_path):
        print(f"Error: {src_path} not found!")
        return
    
    base = Image.open(src_path).convert("RGBA")
    w, h = base.size
    
    # Isolate parts using alpha masks
    def get_part(poly):
        m = Image.new("L", (w, h), 0)
        ImageDraw.Draw(m).polygon(poly, fill=255)
        # Use existing alpha
        base_arr = np.array(base)
        m_arr = np.array(m)
        final_alpha = (base_arr[:, :, 3] * (m_arr / 255.0)).astype(np.uint8)
        part = base.copy()
        part.putalpha(Image.fromarray(final_alpha))
        return part

    # Anatomy polygons
    tail_poly = [(715, 100), (944, 100), (944, 470), (740, 470), (715, 300)]
    head_left_poly = [(0, 40), (380, 40), (370, 450), (220, 480), (0, 480)]
    head_right_poly = [(370, 0), (720, 0), (720, 450), (450, 450), (370, 360)]
    front_left_leg_poly = [(50, 500), (310, 500), (310, 873), (50, 873)]
    front_right_leg_poly = [(430, 510), (690, 510), (690, 873), (430, 873)]
    hind_leg_poly = [(680, 420), (944, 420), (944, 873), (680, 873)]
    torso_poly = [(180, 310), (780, 310), (780, 690), (180, 690)]

    tail_img = get_part(tail_poly)
    head_left_img = get_part(head_left_poly)
    head_right_img = get_part(head_right_poly)
    front_left_leg_img = get_part(front_left_leg_poly)
    front_right_leg_img = get_part(front_right_leg_poly)
    hind_leg_img = get_part(hind_leg_poly)
    torso_img = get_part(torso_poly)

    fw, fh = 340, 300
    scale = 260.0 / max(w, h)
    sw, sh = int(w * scale), int(h * scale)

    # Helper: rotate an image around an anchor point (px, py) in original coordinates
    def transform_part(part_img, angle_deg, dx, dy, anchor_xy):
        ax, ay = anchor_xy
        # Create a larger canvas to avoid clipping
        pad = 120
        pw, ph = w + pad * 2, h + pad * 2
        temp = Image.new("RGBA", (pw, ph), (0,0,0,0))
        temp.paste(part_img, (pad, pad))
        # Rotate around anchor
        rot = temp.rotate(angle_deg, resample=Image.Resampling.BILINEAR, center=(ax + pad, ay + pad))
        # Now translate
        res = Image.new("RGBA", (pw, ph), (0,0,0,0))
        res.paste(rot, (int(dx), int(dy)))
        # Return cropped back
        return res.crop((pad, pad, pad + w, pad + h))

    # --- Generate 8-frame Gallop Walk Sheet ---
    walk_sheet = Image.new("RGBA", (fw * 8, fh), (0,0,0,0))
    for f in range(8):
        phi = f * 2.0 * math.pi / 8.0
        
        # 4-beat gallop / bounding gait
        body_y = -math.sin(phi * 2.0) * 12.0
        body_tilt = math.sin(phi) * 3.5

        # Legs rotation & translation
        fl_rot = math.sin(phi) * 26.0
        fl_dy = -abs(math.sin(phi)) * 14.0 if math.sin(phi) > 0 else 0
        
        fr_rot = math.sin(phi + math.pi * 0.85) * 24.0
        fr_dy = -abs(math.sin(phi + math.pi * 0.85)) * 12.0 if math.sin(phi + math.pi * 0.85) > 0 else 0
        
        hind_rot = math.sin(phi + math.pi * 1.6) * 22.0
        hind_dy = -abs(math.sin(phi + math.pi * 1.6)) * 16.0 if math.sin(phi + math.pi * 1.6) > 0 else 0

        tail_rot = math.sin(phi - 1.2) * 18.0
        
        hl_rot = math.sin(phi * 2.0 + 0.4) * 6.0
        hr_rot = math.sin(phi * 2.0 - 0.4) * 5.0

        # Layer transforms
        t_tail = transform_part(tail_img, tail_rot + body_tilt, 0, body_y, (740, 430))
        t_hind = transform_part(hind_leg_img, hind_rot, 0, body_y + hind_dy, (780, 500))
        t_fr = transform_part(front_right_leg_img, fr_rot, 0, body_y + fr_dy, (580, 550))
        t_torso = transform_part(torso_img, body_tilt, 0, body_y, (450, 500))
        t_fl = transform_part(front_left_leg_img, fl_rot, 0, body_y + fl_dy, (240, 550))
        t_hl = transform_part(head_left_img, hl_rot + body_tilt, 0, body_y, (330, 420))
        t_hr = transform_part(head_right_img, hr_rot + body_tilt, 0, body_y, (460, 380))

        # Composite frame at native resolution
        comp = Image.new("RGBA", (w, h), (0,0,0,0))
        comp.paste(t_tail, (0,0), t_tail)
        comp.paste(t_hind, (0,0), t_hind)
        comp.paste(t_fr, (0,0), t_fr)
        comp.paste(t_torso, (0,0), t_torso)
        comp.paste(t_fl, (0,0), t_fl)
        comp.paste(t_hr, (0,0), t_hr)
        comp.paste(t_hl, (0,0), t_hl)

        # Dynamic Exhaust Flames & Visor Glint
        draw = ImageDraw.Draw(comp)
        # Exhaust flame on back (twin pipes at x~540, y~380)
        flame_len = [0, 14, 38, 48, 30, 10, 0, 8][f]
        if flame_len > 0:
            ex_y = 380 + int(body_y)
            for pipe_x, pipe_y in [(545, ex_y), (585, ex_y - 12)]:
                # Outer orange flame
                draw.polygon([(pipe_x, pipe_y - 12), (pipe_x + flame_len, pipe_y), (pipe_x, pipe_y + 12)], fill=(239, 68, 68, 220))
                # Inner yellow core
                draw.polygon([(pipe_x, pipe_y - 6), (pipe_x + flame_len * 0.7, pipe_y), (pipe_x, pipe_y + 6)], fill=(254, 240, 138, 250))
                # Smoke puff at tip
                if flame_len > 25:
                    draw.ellipse([pipe_x + flame_len - 4, pipe_y - 8, pipe_x + flame_len + 16, pipe_y + 8], fill=(120, 113, 108, 140))

        # Visor gleam
        glint_x = (f * 18) % 70
        draw.line([(140 + glint_x, 180 + body_y), (145 + glint_x, 180 + body_y)], fill=(255, 255, 255, 240), width=3)
        draw.line([(550 + glint_x, 145 + body_y), (555 + glint_x, 145 + body_y)], fill=(255, 255, 255, 240), width=3)

        # Scale down to target frame
        scaled = comp.resize((sw, sh), Image.Resampling.BILINEAR)
        ox = (fw - sw) // 2
        oy = (fh - sh) // 2 + 10
        walk_sheet.paste(scaled, (f * fw + ox, oy), scaled)

    # --- Generate 8-frame Attack Sheet (Lunge / Howl) ---
    attack_sheet = Image.new("RGBA", (fw * 8, fh), (0,0,0,0))
    for f in range(8):
        comp = Image.new("RGBA", (w, h), (0,0,0,0))
        draw = ImageDraw.Draw(comp)
        
        if f <= 2:
            # Windup crouch (anticipation)
            crouch_prog = (f + 1) / 3.0
            by = crouch_prog * 26.0
            t_tail = transform_part(tail_img, -18.0 * crouch_prog, 0, by, (740, 430))
            t_hind = transform_part(hind_leg_img, 15.0 * crouch_prog, 0, by, (780, 500))
            t_fr = transform_part(front_right_leg_img, -14.0 * crouch_prog, 0, by, (580, 550))
            t_torso = transform_part(torso_img, 4.0 * crouch_prog, 0, by, (450, 500))
            t_fl = transform_part(front_left_leg_img, -20.0 * crouch_prog, 0, by, (240, 550))
            t_hl = transform_part(head_left_img, -10.0 * crouch_prog, 0, by, (330, 420))
            t_hr = transform_part(head_right_img, -12.0 * crouch_prog, 0, by, (460, 380))
            
            comp.paste(t_tail, (0,0), t_tail)
            comp.paste(t_hind, (0,0), t_hind)
            comp.paste(t_fr, (0,0), t_fr)
            comp.paste(t_torso, (0,0), t_torso)
            comp.paste(t_fl, (0,0), t_fl)
            comp.paste(t_hr, (0,0), t_hr)
            comp.paste(t_hl, (0,0), t_hl)
            
            # Glowing red charge sparks around heads
            for sx, sy in [(120, 200 + by), (180, 240 + by), (520, 160 + by)]:
                draw.ellipse([sx - 4, sy - 4, sx + 4, sy + 4], fill=(239, 68, 68, 220))
                draw.line([(sx - 8, sy), (sx + 8, sy)], fill=(254, 240, 138, 240), width=2)
        elif f <= 5:
            # Explosive lunge / dash strike
            lunge_prog = (f - 3) / 2.0
            bx = (1.0 - lunge_prog) * -40.0
            by = -15.0 - math.sin(lunge_prog * math.pi) * 20.0
            
            t_tail = transform_part(tail_img, 28.0, bx, by, (740, 430))
            t_hind = transform_part(hind_leg_img, -32.0, bx, by, (780, 500))
            t_fr = transform_part(front_right_leg_img, 36.0, bx, by, (580, 550))
            t_torso = transform_part(torso_img, -10.0, bx, by, (450, 500))
            t_fl = transform_part(front_left_leg_img, 42.0, bx, by, (240, 550))
            t_hl = transform_part(head_left_img, 14.0, bx, by, (330, 420))
            t_hr = transform_part(head_right_img, 12.0, bx, by, (460, 380))
            
            comp.paste(t_tail, (0,0), t_tail)
            comp.paste(t_hind, (0,0), t_hind)
            comp.paste(t_fr, (0,0), t_fr)
            comp.paste(t_torso, (0,0), t_torso)
            comp.paste(t_fl, (0,0), t_fl)
            comp.paste(t_hr, (0,0), t_hr)
            comp.paste(t_hl, (0,0), t_hl)
            
            # Massive afterburner jet
            draw.polygon([(560, 380 + by), (660, 380 + by), (560, 410 + by)], fill=(239, 68, 68, 240))
            draw.polygon([(560, 385 + by), (630, 385 + by), (560, 405 + by)], fill=(254, 240, 138, 255))
            # Slash claws sparks
            draw.arc([40, 680 + by, 180, 820 + by], start=180, end=330, fill=(254, 240, 138, 240), width=4)
        else:
            # Sonic Howl (heads thrown high, mouths wide open)
            howl_prog = (f - 6) / 1.0
            by = -8.0
            t_tail = transform_part(tail_img, -20.0, 0, by, (740, 430))
            t_hind = transform_part(hind_leg_img, 10.0, 0, by, (780, 500))
            t_fr = transform_part(front_right_leg_img, -8.0, 0, by, (580, 550))
            t_torso = transform_part(torso_img, 6.0, 0, by, (450, 500))
            t_fl = transform_part(front_left_leg_img, -12.0, 0, by, (240, 550))
            t_hl = transform_part(head_left_img, -28.0, 0, by, (330, 420))
            t_hr = transform_part(head_right_img, -32.0, 0, by, (460, 380))
            
            comp.paste(t_tail, (0,0), t_tail)
            comp.paste(t_hind, (0,0), t_hind)
            comp.paste(t_fr, (0,0), t_fr)
            comp.paste(t_torso, (0,0), t_torso)
            comp.paste(t_fl, (0,0), t_fl)
            comp.paste(t_hr, (0,0), t_hr)
            comp.paste(t_hl, (0,0), t_hl)
            
            # Sonic shockwave rings emitting from mouths
            for ring_r in [30, 65, 105]:
                draw.arc([100 - ring_r, 120 - ring_r, 100 + ring_r, 120 + ring_r], start=190, end=340, fill=(239, 68, 68, 200), width=3)
                draw.arc([440 - ring_r, 70 - ring_r, 440 + ring_r, 70 + ring_r], start=190, end=340, fill=(244, 63, 94, 200), width=3)

        scaled = comp.resize((sw, sh), Image.Resampling.BILINEAR)
        ox = (fw - sw) // 2
        oy = (fh - sh) // 2 + 10
        attack_sheet.paste(scaled, (f * fw + ox, oy), scaled)

    # Save sheets
    walk_sheet.save(os.path.join(MONSTERS_DIR, "boss_cyber_cerberus_walk.webp"), "WEBP", quality=95)
    walk_sheet.save(os.path.join(MONSTERS_DIR, "boss_cyber_cerberus_sheet.webp"), "WEBP", quality=95)
    attack_sheet.save(os.path.join(MONSTERS_DIR, "boss_cyber_cerberus_attack.webp"), "WEBP", quality=95)
    print("Saved boss_cyber_cerberus sheets successfully!")

# ==============================================================================
# 2. BIO-BUTCHER (Хирург-Мясник)
# ==============================================================================
def generate_bio_butcher_sheets():
    src_path = os.path.join(MONSTERS_DIR, "boss_bio_butcher.webp")
    if not os.path.exists(src_path):
        print(f"Error: {src_path} not found!")
        return

    base = Image.open(src_path).convert("RGBA")
    w, h = base.size

    def get_part(poly):
        m = Image.new("L", (w, h), 0)
        ImageDraw.Draw(m).polygon(poly, fill=255)
        base_arr = np.array(base)
        m_arr = np.array(m)
        final_alpha = (base_arr[:, :, 3] * (m_arr / 255.0)).astype(np.uint8)
        part = base.copy()
        part.putalpha(Image.fromarray(final_alpha))
        return part

    head_poly = [(370, 0), (620, 0), (620, 310), (370, 310)]
    cleaver_poly = [(0, 10), (380, 10), (380, 660), (0, 660)]
    harpoon_poly = [(510, 150), (1006, 150), (1006, 720), (510, 720)]
    boots_left_poly = [(240, 620), (490, 620), (490, 811), (240, 811)]
    boots_right_poly = [(490, 620), (760, 620), (760, 811), (490, 811)]
    torso_poly = [(280, 260), (660, 260), (660, 680), (280, 680)]

    head_img = get_part(head_poly)
    cleaver_img = get_part(cleaver_poly)
    harpoon_img = get_part(harpoon_poly)
    boots_l_img = get_part(boots_left_poly)
    boots_r_img = get_part(boots_right_poly)
    torso_img = get_part(torso_poly)

    fw, fh = 360, 300
    scale = 265.0 / max(w, h)
    sw, sh = int(w * scale), int(h * scale)

    def transform_part(part_img, angle_deg, dx, dy, anchor_xy):
        ax, ay = anchor_xy
        pad = 120
        pw, ph = w + pad * 2, h + pad * 2
        temp = Image.new("RGBA", (pw, ph), (0,0,0,0))
        temp.paste(part_img, (pad, pad))
        rot = temp.rotate(angle_deg, resample=Image.Resampling.BILINEAR, center=(ax + pad, ay + pad))
        res = Image.new("RGBA", (pw, ph), (0,0,0,0))
        res.paste(rot, (int(dx), int(dy)))
        return res.crop((pad, pad, pad + w, pad + h))

    # --- Generate 8-frame Heavy Stomp Walk Sheet ---
    walk_sheet = Image.new("RGBA", (fw * 8, fh), (0,0,0,0))
    for f in range(8):
        phi = f * 2.0 * math.pi / 8.0

        # Heavy lumbering gait: drop down on foot plants (f=1, f=5)
        is_step_l = (f in [0, 1])
        is_step_r = (f in [4, 5])
        body_y = 6.0 if (f == 1 or f == 5) else (0.0 if (f in [0, 4]) else -5.0)
        body_tilt = math.sin(phi) * 4.5

        # Legs stepping
        bl_dy = 0 if is_step_l else -math.sin(phi) * 14.0
        br_dy = 0 if is_step_r else math.sin(phi) * 14.0
        bl_rot = -math.sin(phi) * 8.0
        br_rot = math.sin(phi) * 8.0

        # Cleaver arm rocking
        cleaver_rot = math.sin(phi) * 14.0
        cleaver_dy = body_y + math.sin(phi) * 6.0

        # Mechanical harpoon arm counter-balance
        harpoon_rot = -math.sin(phi) * 10.0
        harpoon_dy = body_y - math.sin(phi) * 5.0

        # Gas mask head bobbing
        head_rot = math.sin(phi) * 3.0
        head_dy = body_y

        t_bl = transform_part(boots_l_img, bl_rot, 0, bl_dy, (360, 680))
        t_br = transform_part(boots_r_img, br_rot, 0, br_dy, (620, 680))
        t_torso = transform_part(torso_img, body_tilt, 0, body_y, (490, 500))
        t_cleaver = transform_part(cleaver_img, cleaver_rot, 0, cleaver_dy, (320, 320))
        t_harpoon = transform_part(harpoon_img, harpoon_rot, 0, harpoon_dy, (620, 320))
        t_head = transform_part(head_img, head_rot, 0, head_dy, (490, 280))

        comp = Image.new("RGBA", (w, h), (0,0,0,0))
        comp.paste(t_bl, (0,0), t_bl)
        comp.paste(t_br, (0,0), t_br)
        comp.paste(t_torso, (0,0), t_torso)
        comp.paste(t_head, (0,0), t_head)
        comp.paste(t_harpoon, (0,0), t_harpoon)
        comp.paste(t_cleaver, (0,0), t_cleaver)

        draw = ImageDraw.Draw(comp)

        # Dripping blood from cleaver saw teeth
        drip_prog = (f * 14) % 45
        drip_x = 75 + math.sin(phi) * 10
        drip_y = 520 + cleaver_dy + drip_prog
        draw.ellipse([drip_x - 3, drip_y - 4, drip_x + 3, drip_y + 4], fill=(220, 38, 38, 240))
        if f in [2, 6]:
            draw.ellipse([drip_x + 25, drip_y - 15, drip_x + 29, drip_y - 10], fill=(185, 28, 28, 220))

        # Toxic green steam puffs from respirator
        steam_prog = (f * 6) % 20
        draw.ellipse([460 - steam_prog, 250 + body_y - steam_prog, 475 + steam_prog, 265 + body_y], fill=(74, 222, 128, 110))

        # Glowing red eye lens flares
        eye_pulse = 0.85 + 0.15 * math.sin(phi * 2.0)
        draw.ellipse([435, 145 + body_y, 447, 157 + body_y], fill=(239, 68, 68, int(255 * eye_pulse)))
        draw.ellipse([495, 145 + body_y, 507, 157 + body_y], fill=(239, 68, 68, int(255 * eye_pulse)))
        draw.point([(441, 151 + body_y), (501, 151 + body_y)], fill=(254, 240, 138, 255))

        scaled = comp.resize((sw, sh), Image.Resampling.BILINEAR)
        ox = (fw - sw) // 2
        oy = (fh - sh) // 2 + 10
        walk_sheet.paste(scaled, (f * fw + ox, oy), scaled)

    # --- Generate 8-frame Attack Sheet (Cleaver Smash / Hook Throw) ---
    attack_sheet = Image.new("RGBA", (fw * 8, fh), (0,0,0,0))
    for f in range(8):
        comp = Image.new("RGBA", (w, h), (0,0,0,0))
        draw = ImageDraw.Draw(comp)

        if f <= 3:
            # Overhead Cleaver Windup & Stomp
            wind_prog = (f + 1) / 4.0
            by = -10.0 * wind_prog
            c_rot = -55.0 * wind_prog
            c_dy = -40.0 * wind_prog
            
            t_bl = transform_part(boots_l_img, 0, 0, 0, (360, 680))
            t_br = transform_part(boots_r_img, -6.0 * wind_prog, 0, 0, (620, 680))
            t_torso = transform_part(torso_img, -6.0 * wind_prog, 0, by, (490, 500))
            t_head = transform_part(head_img, -8.0 * wind_prog, 0, by, (490, 280))
            t_harpoon = transform_part(harpoon_img, 15.0 * wind_prog, 0, by, (620, 320))
            t_cleaver = transform_part(cleaver_img, c_rot, 20.0 * wind_prog, c_dy, (320, 320))

            comp.paste(t_bl, (0,0), t_bl)
            comp.paste(t_br, (0,0), t_br)
            comp.paste(t_torso, (0,0), t_torso)
            comp.paste(t_head, (0,0), t_head)
            comp.paste(t_harpoon, (0,0), t_harpoon)
            comp.paste(t_cleaver, (0,0), t_cleaver)

            # Warning spark on cleaver edge
            draw.line([(80, 160 + c_dy), (95, 175 + c_dy)], fill=(254, 240, 138, 255), width=3)
        elif f <= 5:
            # Massive Cleaver Smash into Floor
            smash_prog = (f - 4) / 1.0
            by = 12.0
            c_rot = 38.0
            c_dy = 30.0

            t_bl = transform_part(boots_l_img, 4.0, 0, 0, (360, 680))
            t_br = transform_part(boots_r_img, 4.0, 0, 0, (620, 680))
            t_torso = transform_part(torso_img, 8.0, 0, by, (490, 500))
            t_head = transform_part(head_img, 10.0, 0, by, (490, 280))
            t_harpoon = transform_part(harpoon_img, -18.0, 0, by, (620, 320))
            t_cleaver = transform_part(cleaver_img, c_rot, -15.0, c_dy, (320, 320))

            comp.paste(t_bl, (0,0), t_bl)
            comp.paste(t_br, (0,0), t_br)
            comp.paste(t_torso, (0,0), t_torso)
            comp.paste(t_head, (0,0), t_head)
            comp.paste(t_harpoon, (0,0), t_harpoon)
            comp.paste(t_cleaver, (0,0), t_cleaver)

            # Impact shockwave and blood splatter on ground
            draw.arc([20, 720, 240, 800], start=180, end=360, fill=(220, 38, 38, 250), width=5)
            draw.line([(40, 760), (10, 730)], fill=(220, 38, 38, 250), width=3)
            draw.line([(180, 760), (220, 730)], fill=(220, 38, 38, 250), width=3)
        else:
            # Harpoon Launch Forward
            h_prog = (f - 6) / 1.0
            t_bl = transform_part(boots_l_img, 0, 0, 0, (360, 680))
            t_br = transform_part(boots_r_img, 0, 0, 0, (620, 680))
            t_torso = transform_part(torso_img, 0, 0, 0, (490, 500))
            t_head = transform_part(head_img, 0, 0, 0, (490, 280))
            t_harpoon = transform_part(harpoon_img, -15.0, 10, 0, (620, 320))
            t_cleaver = transform_part(cleaver_img, 0, 0, 0, (320, 320))

            comp.paste(t_bl, (0,0), t_bl)
            comp.paste(t_br, (0,0), t_br)
            comp.paste(t_torso, (0,0), t_torso)
            comp.paste(t_head, (0,0), t_head)
            comp.paste(t_harpoon, (0,0), t_harpoon)
            comp.paste(t_cleaver, (0,0), t_cleaver)

            # Harpoon projectile & chain links flying
            hx = 880 + int(h_prog * 60)
            draw.polygon([(hx, 510), (hx + 30, 520), (hx, 530)], fill=(220, 38, 38, 255))
            # Chain links
            for cx in range(780, hx, 18):
                draw.ellipse([cx, 516, cx + 12, 524], outline=(200, 200, 200, 240), width=2)

        scaled = comp.resize((sw, sh), Image.Resampling.BILINEAR)
        ox = (fw - sw) // 2
        oy = (fh - sh) // 2 + 10
        attack_sheet.paste(scaled, (f * fw + ox, oy), scaled)

    # Save sheets
    walk_sheet.save(os.path.join(MONSTERS_DIR, "boss_bio_butcher_walk.webp"), "WEBP", quality=95)
    walk_sheet.save(os.path.join(MONSTERS_DIR, "boss_bio_butcher_sheet.webp"), "WEBP", quality=95)
    attack_sheet.save(os.path.join(MONSTERS_DIR, "boss_bio_butcher_attack.webp"), "WEBP", quality=95)
    print("Saved boss_bio_butcher sheets successfully!")

# ==============================================================================
# 3. NEURO-OVERMIND (Нейро-Сверхразум)
# ==============================================================================
def generate_neuro_overmind_sheets():
    src_path = os.path.join(MONSTERS_DIR, "boss_neuro_overmind.webp")
    if not os.path.exists(src_path):
        print(f"Error: {src_path} not found!")
        return

    base = Image.open(src_path).convert("RGBA")
    w, h = base.size

    def get_part(poly):
        m = Image.new("L", (w, h), 0)
        ImageDraw.Draw(m).polygon(poly, fill=255)
        base_arr = np.array(base)
        m_arr = np.array(m)
        final_alpha = (base_arr[:, :, 3] * (m_arr / 255.0)).astype(np.uint8)
        part = base.copy()
        part.putalpha(Image.fromarray(final_alpha))
        return part

    brain_poly = [(310, 110), (660, 110), (660, 480), (310, 480)]
    jar_poly = [(240, 0), (720, 0), (720, 520), (240, 520)]
    chassis_poly = [(180, 490), (780, 490), (780, 760), (180, 760)]
    claw_poly = [(680, 530), (904, 530), (904, 820), (680, 820)]
    legs_poly = [(0, 640), (480, 640), (480, 883), (0, 883)]

    brain_img = get_part(brain_poly)
    # Mask out the brain from the jar to allow independent expansion
    jar_img = get_part(jar_poly)
    chassis_img = get_part(chassis_poly)
    claw_img = get_part(claw_poly)
    legs_img = get_part(legs_poly)

    fw, fh = 320, 320
    scale = 265.0 / max(w, h)
    sw, sh = int(w * scale), int(h * scale)

    def transform_part(part_img, angle_deg, dx, dy, anchor_xy):
        ax, ay = anchor_xy
        pad = 120
        pw, ph = w + pad * 2, h + pad * 2
        temp = Image.new("RGBA", (pw, ph), (0,0,0,0))
        temp.paste(part_img, (pad, pad))
        rot = temp.rotate(angle_deg, resample=Image.Resampling.BILINEAR, center=(ax + pad, ay + pad))
        res = Image.new("RGBA", (pw, ph), (0,0,0,0))
        res.paste(rot, (int(dx), int(dy)))
        return res.crop((pad, pad, pad + w, pad + h))

    # --- Generate 8-frame Levitation / Brain Pulse Sheet ---
    float_sheet = Image.new("RGBA", (fw * 8, fh), (0,0,0,0))
    for f in range(8):
        phi = f * 2.0 * math.pi / 8.0

        # Multi-frequency levitation bob
        pod_y = math.sin(phi) * 10.0 + math.sin(phi * 2.0) * 3.0
        pod_roll = math.sin(phi) * 2.5

        # Brain organic heartbeat expansion & contraction
        # Systolic squeeze and diastolic bloom
        pulse_scale = 1.0 + math.sin(phi * 2.0) * 0.08
        bw_new = int(w * pulse_scale)
        bh_new = int(h * pulse_scale)
        t_brain = brain_img.resize((bw_new, bh_new), Image.Resampling.BILINEAR)
        bx_off = (w - bw_new) // 2
        by_off = (h - bh_new) // 2 + int(pod_y)

        # Alternating mechanical spider legs gait
        leg_rot = math.sin(phi) * 12.0
        leg_dy = pod_y - abs(math.sin(phi)) * 6.0

        # Claw arm breathing / flexing
        claw_rot = -math.sin(phi) * 14.0
        claw_dy = pod_y + math.sin(phi) * 5.0

        t_legs = transform_part(legs_img, leg_rot, 0, leg_dy, (240, 740))
        t_chassis = transform_part(chassis_img, pod_roll, 0, pod_y, (480, 620))
        t_jar = transform_part(jar_img, pod_roll, 0, pod_y, (480, 260))
        t_claw = transform_part(claw_img, claw_rot, 0, claw_dy, (730, 620))

        comp = Image.new("RGBA", (w, h), (0,0,0,0))
        comp.paste(t_legs, (0,0), t_legs)
        comp.paste(t_chassis, (0,0), t_chassis)
        # Paste brain with pod float and pulse
        comp.paste(t_brain, (bx_off, by_off), t_brain)
        comp.paste(t_jar, (0,0), t_jar)
        comp.paste(t_claw, (0,0), t_claw)

        draw = ImageDraw.Draw(comp)

        # Writhing bio-cables underneath chassis
        for tent_i in range(-3, 4):
            if tent_i == 0: continue
            tx = 480 + tent_i * 35
            ty = 730 + pod_y
            w1 = math.sin(phi * 1.5 + tent_i) * 18.0
            w2 = math.cos(phi * 2.0 + tent_i) * 26.0
            points = [(tx, ty), (tx + w1, ty + 40), (tx + w2, ty + 85)]
            draw.line(points, fill=(168, 85, 247, 240), width=4)
            draw.ellipse([tx + w2 - 3, ty + 85 - 3, tx + w2 + 3, ty + 85 + 3], fill=(216, 180, 254, 255))

        # Rising bubbles inside glass cylinder
        for b in range(5):
            bub_t = (f * 12 + b * 18) % 75
            bx = 420 + math.sin(b * 2.0 + phi) * 45
            by = 420 + pod_y - bub_t
            draw.ellipse([bx - 3, by - 3, bx + 3, by + 3], fill=(236, 72, 153, 200))
            draw.point([(bx - 1, by - 1)], fill=(255, 255, 255, 255))

        # Central mechanical eye pupil scanning
        eye_angles = [0, -0.35, -0.65, -0.2, 0.2, 0.65, 0.35, 0]
        ea = eye_angles[f]
        pupil_dist = 6.0
        pex = 550 + math.cos(ea) * pupil_dist + (bx_off * 0.1)
        pey = 285 + math.sin(ea) * pupil_dist + by_off
        draw.ellipse([pex - 5, pey - 5, pex + 5, pey + 5], fill=(239, 68, 68, 255))
        draw.ellipse([pex - 2, pey - 2, pex + 2, pey + 2], fill=(254, 240, 138, 255))

        # 3 Side Indicator lights cycling
        lit_i = f % 3
        for li, (lx, ly) in enumerate([(600, 580 + pod_y), (630, 560 + pod_y), (655, 590 + pod_y)]):
            col = (239, 68, 68, 255) if li == lit_i else (75, 85, 99, 200)
            draw.ellipse([lx - 5, ly - 5, lx + 5, ly + 5], fill=col)

        scaled = comp.resize((sw, sh), Image.Resampling.BILINEAR)
        ox = (fw - sw) // 2
        oy = (fh - sh) // 2 + 10
        float_sheet.paste(scaled, (f * fw + ox, oy), scaled)

    # --- Generate 8-frame Psychic Blast / Singularity Sheet ---
    attack_sheet = Image.new("RGBA", (fw * 8, fh), (0,0,0,0))
    for f in range(8):
        comp = Image.new("RGBA", (w, h), (0,0,0,0))
        draw = ImageDraw.Draw(comp)

        if f <= 3:
            # Psychic overcharge: Brain expands and radiates purple aura
            charge_prog = (f + 1) / 4.0
            pulse_scale = 1.0 + charge_prog * 0.18
            bw_new = int(w * pulse_scale)
            bh_new = int(h * pulse_scale)
            t_brain = brain_img.resize((bw_new, bh_new), Image.Resampling.BILINEAR)
            bx_off = (w - bw_new) // 2
            by_off = (h - bh_new) // 2 - int(charge_prog * 12.0)

            t_legs = transform_part(legs_img, 0, 0, -charge_prog * 8.0, (240, 740))
            t_chassis = transform_part(chassis_img, 0, 0, -charge_prog * 8.0, (480, 620))
            t_jar = transform_part(jar_img, 0, 0, -charge_prog * 8.0, (480, 260))
            t_claw = transform_part(claw_img, 28.0 * charge_prog, 0, -charge_prog * 8.0, (730, 620))

            comp.paste(t_legs, (0,0), t_legs)
            comp.paste(t_chassis, (0,0), t_chassis)
            comp.paste(t_brain, (bx_off, by_off), t_brain)
            comp.paste(t_jar, (0,0), t_jar)
            comp.paste(t_claw, (0,0), t_claw)

            # Brilliant psychic aura & lightning arcs
            for arc_i in range(4):
                ax1 = 340 + arc_i * 80
                ay1 = 120 - charge_prog * 8.0
                ax2 = ax1 + (math.sin(f + arc_i) * 35)
                ay2 = ay1 + 160
                draw.line([(ax1, ay1), ((ax1+ax2)/2 + 20, (ay1+ay2)/2), (ax2, ay2)], fill=(236, 72, 153, 240), width=3)
        else:
            # Singularity blast: Violent psychic burst rings
            burst_prog = (f - 4) / 3.0
            by_off = (h - h) // 2

            t_legs = transform_part(legs_img, -8.0 * (1 - burst_prog), 0, 0, (240, 740))
            t_chassis = transform_part(chassis_img, 0, 0, 0, (480, 620))
            t_jar = transform_part(jar_img, 0, 0, 0, (480, 260))
            t_claw = transform_part(claw_img, -18.0 * (1 - burst_prog), 0, 0, (730, 620))

            comp.paste(t_legs, (0,0), t_legs)
            comp.paste(t_chassis, (0,0), t_chassis)
            comp.paste(brain_img, (0,0), brain_img)
            comp.paste(t_jar, (0,0), t_jar)
            comp.paste(t_claw, (0,0), t_claw)

            # Expanding psychic shockwave rings
            ring_r = int(50 + burst_prog * 240)
            draw.ellipse([480 - ring_r, 300 - ring_r, 480 + ring_r, 300 + ring_r], outline=(168, 85, 247, int(255 * (1 - burst_prog))), width=6)
            draw.ellipse([480 - ring_r * 0.7, 300 - ring_r * 0.7, 480 + ring_r * 0.7, 300 + ring_r * 0.7], outline=(236, 72, 153, int(220 * (1 - burst_prog))), width=4)

        scaled = comp.resize((sw, sh), Image.Resampling.BILINEAR)
        ox = (fw - sw) // 2
        oy = (fh - sh) // 2 + 10
        attack_sheet.paste(scaled, (f * fw + ox, oy), scaled)

    # Save sheets
    float_sheet.save(os.path.join(MONSTERS_DIR, "boss_neuro_overmind_float.webp"), "WEBP", quality=95)
    float_sheet.save(os.path.join(MONSTERS_DIR, "boss_neuro_overmind_sheet.webp"), "WEBP", quality=95)
    attack_sheet.save(os.path.join(MONSTERS_DIR, "boss_neuro_overmind_attack.webp"), "WEBP", quality=95)
    print("Saved boss_neuro_overmind sheets successfully!")

if __name__ == "__main__":
    print("Starting generation of all boss spritesheets...")
    generate_cyber_cerberus_sheets()
    generate_bio_butcher_sheets()
    generate_neuro_overmind_sheets()
    print("All spritesheets generated successfully!")
