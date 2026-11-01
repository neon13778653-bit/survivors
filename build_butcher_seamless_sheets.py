import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

CANVAS_W = 360
CANVAS_H = 300
WORK_S = 400

SCALE = 0.60
TARGET_W = int(WORK_S * SCALE)  # 240
TARGET_H = int(WORK_S * SCALE)  # 240
OFFSET_X = 60
OFFSET_Y = 32


def load_work_img(path):
    im = Image.open(path).convert("RGBA")
    return im.resize((WORK_S, WORK_S), Image.Resampling.LANCZOS)


def make_soft_mask(polygons, blur_radius=5, size=WORK_S):
    m = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(m)
    for poly in polygons:
        d.polygon(poly, fill=255)
    if blur_radius > 0:
        m = m.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    return np.asarray(m, dtype=np.float32) / 255.0


def make_radial_mask(cx, cy, rx, ry, blur_radius=6, size=WORK_S):
    y_grid, x_grid = np.mgrid[0:size, 0:size].astype(np.float32)
    dist = np.sqrt(((x_grid - cx) / max(1.0, rx)) ** 2 + ((y_grid - cy) / max(1.0, ry)) ** 2)
    w = np.clip(1.0 - dist, 0.0, 1.0)
    w = w * w * (3.0 - 2.0 * w)
    if blur_radius > 0:
        im = Image.fromarray((w * 255).astype(np.uint8), mode="L")
        im = im.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        w = np.asarray(im, dtype=np.float32) / 255.0
    return w


def sample_weighted_layer(src_arr, src_weight, dx, dy):
    h, w, _ = src_arr.shape
    y_grid, x_grid = np.mgrid[0:h, 0:w].astype(np.float32)

    sx = x_grid - dx
    sy = y_grid - dy
    in_bounds = ((sx >= 0.0) & (sx < w - 1.001) & (sy >= 0.0) & (sy < h - 1.001)).astype(np.float32)

    sx_c = np.clip(sx, 0.0, w - 1.001)
    sy_c = np.clip(sy, 0.0, h - 1.001)

    x0 = np.floor(sx_c).astype(np.int32)
    y0 = np.floor(sy_c).astype(np.int32)
    x1 = np.minimum(x0 + 1, w - 1)
    y1 = np.minimum(y0 + 1, h - 1)

    fx = (sx_c - x0)[..., None]
    fy = (sy_c - y0)[..., None]

    c00 = src_arr[y0, x0]
    c10 = src_arr[y0, x1]
    c01 = src_arr[y1, x0]
    c11 = src_arr[y1, x1]

    m00 = src_weight[y0, x0][..., None]
    m10 = src_weight[y0, x1][..., None]
    m01 = src_weight[y1, x0][..., None]
    m11 = src_weight[y1, x1][..., None]

    a00 = (c00[..., 3:4] / 255.0) * m00
    a10 = (c10[..., 3:4] / 255.0) * m10
    a01 = (c01[..., 3:4] / 255.0) * m01
    a11 = (c11[..., 3:4] / 255.0) * m11

    ib = in_bounds[..., None]
    w00 = (1.0 - fx) * (1.0 - fy)
    w10 = fx * (1.0 - fy)
    w01 = (1.0 - fx) * fy
    w11 = fx * fy

    alpha_part = (w00 * a00 + w10 * a10 + w01 * a01 + w11 * a11) * ib
    rgb_premult = (
        w00 * a00 * c00[..., :3]
        + w10 * a10 * c10[..., :3]
        + w01 * a01 * c01[..., :3]
        + w11 * a11 * c11[..., :3]
    ) * ib

    return rgb_premult, alpha_part


def composite_skinned_layers(src_img, layers):
    src_arr = np.asarray(src_img, dtype=np.float32)
    h, w, _ = src_arr.shape
    total_rgb = np.zeros((h, w, 3), dtype=np.float32)
    total_alpha = np.zeros((h, w, 1), dtype=np.float32)

    for src_weight, dx, dy in layers:
        rgb_p, a_p = sample_weighted_layer(src_arr, src_weight, dx, dy)
        total_rgb += rgb_p
        total_alpha += a_p

    rgb = np.where(total_alpha > 0.05, total_rgb / np.maximum(total_alpha, 1e-4), 0.0)
    alpha = np.where(total_alpha > 0.35, 255.0, 0.0)
    out = np.concatenate([np.clip(rgb, 0, 255), alpha], axis=-1).astype(np.uint8)
    return Image.fromarray(out, mode="RGBA")


def rotation_field(px, py, angle_deg, base_dx=0.0, base_dy=0.0, size=WORK_S):
    y_grid, x_grid = np.mgrid[0:size, 0:size].astype(np.float32)
    rad = math.radians(angle_deg)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)

    rx = x_grid - px
    ry = y_grid - py
    dx = base_dx + (rx * (cos_a - 1.0) - ry * sin_a)
    dy = base_dy + (rx * sin_a + ry * (cos_a - 1.0))
    return dx, dy


def finalize_frame(work_img, extra_dx=0, extra_dy=0):
    scaled = work_img.resize((TARGET_W, TARGET_H), Image.Resampling.NEAREST)
    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    canvas.alpha_composite(scaled, (OFFSET_X + int(round(extra_dx)), OFFSET_Y + int(round(extra_dy))))
    return canvas


def build_bio_butcher_sheets():
    base = load_work_img("img/monsters/boss_bio_butcher.webp")

    # Precise Anatomical Soft Masks (strictly non-conflicting, feathered at joints):
    # 1. Screen-Left Arm with Chainsaw:
    #    Shoulder pivot at (145, 115). Hand at (115, 205).
    #    Chainsaw motor at (95, 240), blade down-left to (0, 335).
    m_arm_saw = make_soft_mask(
        [[(0, 160), (155, 95), (155, 235), (120, 275), (0, 360)]], blur_radius=5
    )
    m_saw_blade = make_soft_mask(
        [[(0, 200), (120, 200), (110, 280), (0, 360)]], blur_radius=5
    )

    # 2. Screen-Right Arm: Cybernetic Pneumatic Harpoon Cannon:
    #    Shoulder pivot at (268, 105).
    #    Strictly starts at x >= 290 below y=240 so it NEVER intersects the right boot!
    m_arm_harpoon = make_soft_mask(
        [[(250, 60), (399, 60), (399, 399), (292, 399), (292, 245), (250, 175)]],
        blur_radius=5,
    )
    m_harpoon_forearm = make_soft_mask(
        [[(280, 175), (399, 175), (399, 399), (292, 399)]], blur_radius=5
    )

    # 3. Screen-Left Leg (Butcher's right leg):
    #    Hip at (165, 270), knee at (155, 310), boot at (115..205, 305..385)
    m_leg_left = make_soft_mask(
        [[(112, 268), (195, 268), (205, 386), (112, 386)]], blur_radius=5
    )
    m_shin_left = make_soft_mask(
        [[(112, 305), (195, 305), (205, 386), (112, 386)]], blur_radius=5
    )

    # 4. Screen-Right Leg (Butcher's left leg):
    #    Hip at (235, 270), knee at (255, 310), boot at (225..290, 305..399)
    #    Strictly bounded at x <= 290 so it NEVER touches the harpoon cannon!
    m_leg_right = make_soft_mask(
        [[(200, 268), (290, 268), (290, 399), (220, 399)]], blur_radius=5
    )
    m_shin_right = make_soft_mask(
        [[(200, 305), (290, 305), (290, 399), (220, 399)]], blur_radius=5
    )

    # 5. Head & Gas Mask:
    #    Neck pivot at (200, 100)
    m_head = make_soft_mask(
        [[(160, 0), (248, 0), (248, 105), (160, 105)]], blur_radius=5
    )

    # Normalize partition of unity: sum(limbs) + m_torso == 1.0 everywhere
    limbs = [m_arm_saw, m_arm_harpoon, m_leg_left, m_leg_right, m_head]
    lsum = np.sum(limbs, axis=0)
    lscale = np.where(lsum > 1.0, 1.0 / np.maximum(lsum, 1e-5), 1.0)
    m_arm_saw *= lscale
    m_arm_harpoon *= lscale
    m_leg_left *= lscale
    m_leg_right *= lscale
    m_head *= lscale
    m_torso = np.clip(1.0 - (m_arm_saw + m_arm_harpoon + m_leg_left + m_leg_right + m_head), 0.0, 1.0)

    # Belly / apron breathing expansion mask
    mask_belly = make_radial_mask(205, 210, 55, 65, blur_radius=8)
    y_grid, x_grid = np.mgrid[0:WORK_S, 0:WORK_S].astype(np.float32)

    def render_butcher_pose(
        body_dx_val,
        body_dy_val,
        saw_arm_ang,
        saw_blade_vib_x,
        saw_blade_vib_y,
        harpoon_arm_ang,
        harpoon_forearm_ang,
        leg_l_ang,
        shin_l_ang,
        leg_l_lift,
        leg_r_ang,
        shin_r_ang,
        leg_r_lift,
        head_ang,
        breath_scale=0.0,
    ):
        t_dx = np.full((WORK_S, WORK_S), body_dx_val, dtype=np.float32)
        t_dy = np.full((WORK_S, WORK_S), body_dy_val, dtype=np.float32)

        if breath_scale != 0.0:
            t_dx += mask_belly * ((x_grid - 205.0) / 55.0) * breath_scale
            t_dy += mask_belly * ((y_grid - 210.0) / 65.0) * breath_scale

        layers = [(m_torso, t_dx, t_dy)]

        # 1. Chainsaw Arm rotates around shoulder (145, 115) + blade engine vibration
        sa_dx, sa_dy = rotation_field(145, 115, saw_arm_ang, t_dx, t_dy)
        if saw_blade_vib_x != 0.0 or saw_blade_vib_y != 0.0:
            sa_dx += m_saw_blade * saw_blade_vib_x
            sa_dy += m_saw_blade * saw_blade_vib_y
        layers.append((m_arm_saw, sa_dx, sa_dy))

        # 2. Harpoon Arm rotates around cyber-shoulder (268, 105) + forearm around (305, 185)
        ha_dx, ha_dy = rotation_field(268, 105, harpoon_arm_ang, t_dx, t_dy)
        if harpoon_forearm_ang != 0.0:
            hf_dx, hf_dy = rotation_field(305, 185, harpoon_forearm_ang, 0.0, 0.0)
            ha_dx += m_harpoon_forearm * hf_dx
            ha_dy += m_harpoon_forearm * hf_dy
        layers.append((m_arm_harpoon, ha_dx, ha_dy))

        # 3. Left Leg rotates around hip (165, 270) + knee (155, 310) + step lift
        ll_dx, ll_dy = rotation_field(165, 270, leg_l_ang, t_dx, t_dy + leg_l_lift)
        if shin_l_ang != 0.0:
            sl_dx, sl_dy = rotation_field(155, 310, shin_l_ang, 0.0, 0.0)
            ll_dx += m_shin_left * sl_dx
            ll_dy += m_shin_left * sl_dy
        layers.append((m_leg_left, ll_dx, ll_dy))

        # 4. Right Leg rotates around hip (235, 270) + knee (255, 310) + step lift
        lr_dx, lr_dy = rotation_field(235, 270, leg_r_ang, t_dx, t_dy + leg_r_lift)
        if shin_r_ang != 0.0:
            sr_dx, sr_dy = rotation_field(255, 310, shin_r_ang, 0.0, 0.0)
            lr_dx += m_shin_right * sr_dx
            lr_dy += m_shin_right * sr_dy
        layers.append((m_leg_right, lr_dx, lr_dy))

        # 5. Head rotates around neck (200, 100)
        hd_dx, hd_dy = rotation_field(200, 100, head_ang, t_dx, t_dy)
        layers.append((m_head, hd_dx, hd_dy))

        return composite_skinned_layers(base, layers)

    # ---------------- WALK (8 FRAMES) ----------------
    walk_frames = []
    for f in range(8):
        phase = (f / 8.0) * 2.0 * math.pi
        sway_x = math.sin(phase) * 3.5
        bob_y = abs(math.sin(phase)) * 4.5 - 2.0

        stride = math.sin(phase)
        l_lift = max(0.0, stride)
        r_lift = max(0.0, -stride)

        # Realistic heavy bipedal walk: leg swing + knee bend on the lifted leg
        leg_l_ang = stride * 12.0
        shin_l_ang = -l_lift * 10.0
        leg_l_lift = -l_lift * 7.0

        leg_r_ang = -stride * 12.0
        shin_r_ang = r_lift * 10.0
        leg_r_lift = -r_lift * 7.0

        # Counter-swinging arms: heavy chainsaw revving vs swinging pneumatic harpoon
        saw_arm_ang = -stride * 10.0
        vib_x = (1.5 if (f % 2 == 0) else -1.5)
        vib_y = (1.0 if (f % 2 == 1) else -1.0)
        harpoon_arm_ang = stride * 9.0
        harpoon_forearm_ang = math.sin(phase - 0.5) * 6.0

        head_ang = math.sin(phase) * 3.5
        breath = math.sin(phase) * 3.0

        warped = render_butcher_pose(
            sway_x,
            bob_y,
            saw_arm_ang,
            vib_x,
            vib_y,
            harpoon_arm_ang,
            harpoon_forearm_ang,
            leg_l_ang,
            shin_l_ang,
            leg_l_lift,
            leg_r_ang,
            shin_r_ang,
            leg_r_lift,
            head_ang,
            breath_scale=breath,
        )

        draw = ImageDraw.Draw(warped)
        # Running chainsaw chain sparks at tip
        spark_x = 45 + int(sway_x - saw_arm_ang * 0.4)
        spark_y = 280 + int(bob_y)
        draw.rectangle([spark_x - 2, spark_y - 2, spark_x + 2, spark_y + 2], fill=(255, 200, 60, 220))
        draw.rectangle([spark_x - 1, spark_y - 1, spark_x + 1, spark_y + 1], fill=(255, 255, 220, 255))

        # Stomp dust puffs on ground contact frames (f == 1 and f == 5)
        if f in (1, 5):
            foot_x = 160 if f == 1 else 265
            foot_y = 384
            for ox, oy, r in [(-14, 2, 6), (0, 4, 8), (14, 2, 6)]:
                draw.ellipse(
                    [foot_x + ox - r, foot_y + oy - r // 2, foot_x + ox + r, foot_y + oy + r // 2],
                    fill=(80, 50, 40, 170),
                )

        walk_frames.append(finalize_frame(warped))

    # ---------------- ATTACK (8 FRAMES) ----------------
    attack_frames = []
    for f in range(8):
        vfx = Image.new("RGBA", (WORK_S, WORK_S), (0, 0, 0, 0))
        vd = ImageDraw.Draw(vfx)
        fx_mode = None

        if f == 0:
            # Frame 0: Chainsaw lift — lifts saw high (-18 deg), body rears back
            warped = render_butcher_pose(
                2.0, -4.0, -18.0, 1.0, -1.0, 8.0, 0.0, -4.0, 0.0, 0.0, 4.0, 0.0, 0.0, -4.0
            )
            fx_mode = "saw_rev_1"

        elif f == 1:
            # Frame 1: Chainsaw cocked back high (-28 deg), motor roaring
            warped = render_butcher_pose(
                4.0, -6.0, -28.0, -2.0, 2.0, 10.0, -4.0, -5.0, 0.0, 0.0, 5.0, 0.0, 0.0, -6.0
            )
            fx_mode = "saw_rev_2"

        elif f == 2:
            # Frame 2: Maximum revving backswing (-36 deg), sparks along saw teeth
            warped = render_butcher_pose(
                5.0, -7.0, -36.0, 2.5, -2.5, 12.0, -5.0, -6.0, 0.0, 0.0, 6.0, 0.0, 0.0, -8.0
            )
            fx_mode = "saw_rev_3"

        elif f == 3:
            # Frame 3: Pre-strike tensing — slight forward lean, saw poised to cleave
            warped = render_butcher_pose(
                1.0, -2.0, -24.0, -2.0, 2.0, 8.0, 0.0, -2.0, 0.0, 0.0, 2.0, 0.0, 0.0, -4.0
            )
            fx_mode = "saw_rev_4"

        elif f == 4:
            # Frame 4: Cleaver Slam Strike! Chainsaw plunges down-left (+24 deg), body lunges down-forward
            warped = render_butcher_pose(
                -8.0, 8.0, 22.0, 1.0, -1.0, -14.0, 8.0, 6.0, -3.0, -3.0, -6.0, 3.0, 3.0, 7.0
            )
            fx_mode = "saw_strike"

        elif f == 5:
            # Frame 5: Strike follow-through & floor grind, sparks spray from blade
            warped = render_butcher_pose(
                -4.0, 5.0, 15.0, -2.0, 2.0, -10.0, 5.0, 3.0, 0.0, 0.0, -3.0, 0.0, 0.0, 3.0
            )
            fx_mode = "saw_follow"

        elif f == 6:
            # Frame 6: Pneumatic Harpoon Aim — cybernetic cannon arm raises forward (-18 deg)
            warped = render_butcher_pose(
                -2.0, -1.0, 6.0, 0.0, 0.0, -18.0, -10.0, 2.0, 0.0, 0.0, -2.0, 0.0, 0.0, 3.0
            )
            fx_mode = "hook_aim"

        else:
            # Frame 7: Pneumatic Harpoon Fire! Arm recoils back, harpoon blasts out with smoke ring & chain
            warped = render_butcher_pose(
                3.0, -2.0, 5.0, 0.0, 0.0, -22.0, -14.0, -2.0, 0.0, 0.0, 2.0, 0.0, 0.0, -2.0
            )
            fx_mode = "hook_fire"

        # Clean, high-impact pixel-art combat VFX overlays
        if fx_mode in ("saw_rev_1", "saw_rev_2", "saw_rev_3", "saw_rev_4"):
            # Glowing red lenses eye flare
            for ex, ey in [(186, 45), (216, 45)]:
                vd.ellipse([ex - 4, ey - 4, ex + 4, ey + 4], fill=(255, 40, 40, 220))
                vd.ellipse([ex - 1, ey - 1, ex + 1, ey + 1], fill=(255, 240, 240, 255))
            # Sparks along the running chainsaw blade
            ang = -18.0 if fx_mode == "saw_rev_1" else (-28.0 if fx_mode == "saw_rev_2" else (-36.0 if fx_mode == "saw_rev_3" else -24.0))
            rad = math.radians(ang)
            for dist in [115, 145, 175]:
                sx = int(145 + math.cos(rad + 2.3) * dist)
                sy = int(115 + math.sin(rad + 2.3) * dist)
                vd.rectangle([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 150, 30, 240))
                vd.rectangle([sx - 1, sy - 1, sx + 1, sy + 1], fill=(255, 255, 210, 255))

        elif fx_mode == "saw_strike":
            # Massive bloody crimson-orange crescent cleave slash arc across the chainsaw path
            for offset, col, w_arc in [
                (0, (185, 15, 25, 245), 20),
                (5, (255, 55, 30, 255), 11),
                (10, (255, 215, 120, 255), 4),
            ]:
                vd.arc(
                    [10 + offset, 115 + offset, 235 - offset, 385 - offset],
                    start=85,
                    end=220,
                    fill=col,
                    width=w_arc,
                )
            for bx, by, br in [(28, 320, 6), (15, 280, 5), (45, 350, 7), (22, 360, 5)]:
                vd.ellipse([bx - br, by - br, bx + br, by + br], fill=(160, 10, 15, 240))
                vd.ellipse([bx - br // 2, by - br // 2, bx + br // 2, by + br // 2], fill=(240, 80, 60, 255))
            for sx, sy in [(35, 335), (18, 305), (55, 365), (75, 380)]:
                vd.rectangle([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 220, 90, 255))

        elif fx_mode == "saw_follow":
            vd.arc([14, 130, 230, 385], start=95, end=210, fill=(220, 35, 35, 175), width=8)
            for sx, sy in [(32, 355), (52, 370), (72, 380)]:
                vd.rectangle([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 180, 50, 210))

        elif fx_mode == "hook_aim":
            # Red targeting laser dot from cannon muzzle & steam puffs from pneumatic valves
            mx, my = 360, 280
            vd.line([(mx, my), (mx + 22, my + 30)], fill=(255, 30, 30, 230), width=2)
            vd.ellipse([mx - 3, my - 3, mx + 3, my + 3], fill=(255, 240, 240, 255))
            # Industrial steam venting from top exhaust ports
            for px, py, r in [(285, 155, 5), (292, 142, 7), (300, 130, 9)]:
                vd.ellipse([px - r, py - r, px + r, py + r], fill=(210, 220, 230, 160))

        elif fx_mode == "hook_fire":
            # High-pressure pneumatic launch! Fiery muzzle blast + flying barbed steel hook with chain
            mx, my = 360, 280
            hx, hy = 394, 335
            # Fiery propellant blast at muzzle
            vd.ellipse([mx - 12, my - 12, mx + 12, my + 12], fill=(255, 120, 30, 230))
            vd.ellipse([mx - 6, my - 6, mx + 6, my + 6], fill=(255, 240, 180, 255))
            # Heavy steel chain links
            vd.line([(mx, my), (hx, hy)], fill=(60, 55, 50, 240), width=5)
            vd.line([(mx, my), (hx, hy)], fill=(180, 175, 170, 255), width=2)
            # Barbed heavy steel anchor hook
            vd.polygon(
                [(hx + 4, hy + 2), (hx - 6, hy - 10), (hx - 2, hy), (hx - 8, hy + 8)],
                fill=(210, 215, 225, 255),
                outline=(40, 40, 45, 255)
            )

        warped = Image.alpha_composite(warped, vfx)
        attack_frames.append(finalize_frame(warped))

    # Save 2880x300 sprite sheets
    save_sheet(walk_frames, "img/monsters/boss_bio_butcher_walk.webp")
    save_sheet(walk_frames, "img/monsters/boss_bio_butcher_sheet.webp")
    save_sheet(attack_frames, "img/monsters/boss_bio_butcher_attack.webp")
    return walk_frames, attack_frames


def save_sheet(frames, out_path):
    sheet = Image.new("RGBA", (CANVAS_W * len(frames), CANVAS_H), (0, 0, 0, 0))
    for i, fr in enumerate(frames):
        sheet.paste(fr, (i * CANVAS_W, 0))
    sheet.save(out_path, "WEBP", lossless=True, quality=100)
    print(f"Saved {out_path} ({sheet.size[0]}x{sheet.size[1]})")


def save_verification_contact_sheet(walk_frames, attack_frames, out_png):
    cols = 4
    rows = 4
    pad = 6
    w = cols * (CANVAS_W + pad) + pad
    h = rows * (CANVAS_H + pad) + pad
    canvas = Image.new("RGBA", (w, h), (24, 20, 26, 255))
    d = ImageDraw.Draw(canvas)

    all_frames = walk_frames + attack_frames
    for idx, fr in enumerate(all_frames):
        c = idx % cols
        r = idx // cols
        x = pad + c * (CANVAS_W + pad)
        y = pad + r * (CANVAS_H + pad)
        label = f"Walk {idx}" if idx < 8 else f"Atk {idx - 8}"
        d.rectangle([x, y, x + CANVAS_W - 1, y + CANVAS_H - 1], fill=(36, 30, 40, 255), outline=(70, 60, 80, 255))
        canvas.alpha_composite(fr, (x, y))
        d.text((x + 8, y + 6), label, fill=(255, 255, 150, 220))

    canvas.save(out_png)
    print(f"Saved verification contact sheet: {out_png}")


def save_gif(frames, out_gif, duration=105):
    bg_frames = []
    for fr in frames:
        bg = Image.new("RGBA", (CANVAS_W, CANVAS_H), (24, 18, 22, 255))
        bg.alpha_composite(fr)
        bg_frames.append(bg.convert("RGB"))
    bg_frames[0].save(
        out_gif,
        save_all=True,
        append_images=bg_frames[1:],
        duration=duration,
        loop=0,
    )
    print(f"Saved GIF: {out_gif}")


if __name__ == "__main__":
    w_frames, a_frames = build_bio_butcher_sheets()
    save_verification_contact_sheet(w_frames, a_frames, "verify_butcher_new.png")

    artifact_dir = r"C:\Users\alexg\.gemini\antigravity\brain\5530d3d0-498e-42f4-b6db-b83d90eb69a6"
    save_gif(w_frames, rf"{artifact_dir}\boss_bio_butcher_new_walk.gif", duration=105)
    save_gif(a_frames, rf"{artifact_dir}\boss_bio_butcher_new_attack.gif", duration=115)
