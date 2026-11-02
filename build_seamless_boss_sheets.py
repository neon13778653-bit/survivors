import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

CANVAS_W = 280
CANVAS_H = 280
WORK_S = 400


def load_work_img(path):
    im = Image.open(path).convert("RGBA")
    return im.resize((WORK_S, WORK_S), Image.Resampling.NEAREST)


def make_soft_mask(polygons, blur_radius=10, size=WORK_S):
    """Creates a smooth [0.0 .. 1.0] weight mask from a list of polygons."""
    m = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(m)
    for poly in polygons:
        d.polygon(poly, fill=255)
    if blur_radius > 0:
        m = m.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    return np.asarray(m, dtype=np.float32) / 255.0


def make_radial_mask(cx, cy, rx, ry, blur_radius=8, size=WORK_S):
    """Creates a smooth elliptical weight mask centered at (cx, cy)."""
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
    """
    Samples `(src_arr * src_weight)` at inverse-mapped coordinates `(x - dx, y - dy)`.
    Returns `(premultiplied_rgb, weighted_alpha)` as float32 arrays.
    """
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

    w00 = (1.0 - fx) * (1.0 - fy)
    w10 = fx * (1.0 - fy)
    w01 = (1.0 - fx) * fy
    w11 = fx * fy

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
    alpha_part = (w00 * a00 + w10 * a10 + w01 * a01 + w11 * a11) * ib
    rgb_premult = (
        w00 * a00 * c00[..., :3]
        + w10 * a10 * c10[..., :3]
        + w01 * a01 * c01[..., :3]
        + w11 * a11 * c11[..., :3]
    ) * ib

    return rgb_premult, alpha_part


def composite_skinned_layers(src_img, layers):
    """
    Dual-Domain Skinned Layer Warping:
    Each item in `layers` is `(src_weight, dx, dy)`.
    Because `sum(src_weight) == 1.0` on the source image and each limb's displacement
    agrees with the body's displacement at its joint pivot (where `src_weight` transitions),
    joints are 100% seamless while limbs never ghost or sample neighboring body parts!
    """
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
    """
    Returns global (dx, dy) over the whole 400x400 canvas that rotates around (px, py)
    by `angle_deg` on top of `(base_dx, base_dy)`.
    At (px, py), the rotational displacement is identically (0, 0)!
    """
    y_grid, x_grid = np.mgrid[0:size, 0:size].astype(np.float32)
    rad = math.radians(angle_deg)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)

    rx = x_grid - px
    ry = y_grid - py
    # Inverse mapping: if forward rotation is +angle_deg, x_new - x = rx*(cos - 1) - ry*sin
    dx = base_dx + (rx * (cos_a - 1.0) - ry * sin_a)
    dy = base_dy + (rx * sin_a + ry * (cos_a - 1.0))
    return dx, dy


SAFE_INNER_W = 256
SAFE_INNER_H = 256
PAD_X = (CANVAS_W - SAFE_INNER_W) // 2
PAD_Y = (CANVAS_H - SAFE_INNER_H) // 2

def finalize_frame(work_img, canvas_dx=0, canvas_dy=0):
    scaled = work_img.resize((SAFE_INNER_W, SAFE_INNER_H), Image.Resampling.BILINEAR)
    out = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    px = int(round(PAD_X + canvas_dx))
    py = int(round(PAD_Y + canvas_dy))
    out.paste(scaled, (px, py), scaled)
    return out


# ==============================================================================
# 1. CHITIN REAPER (Хитиновый Жнец) - DUAL-DOMAIN SKINNED MESH ANIMATIONS
# ==============================================================================
def build_chitin_reaper_sheets():
    base = load_work_img("img/monsters/boss_chitin_reaper.webp")

    # Source-domain limb masks (feathered at joints, strictly disjoint):
    # 1. Upper-left mandible pincer: jaw pivot at (105, 225)
    m_pincer_ul = make_soft_mask(
        [[(102, 212), (4, 212), (4, 362), (88, 305)]], blur_radius=8
    )
    # 2. Lower-right mandible pincer: jaw pivot at (185, 275)
    m_pincer_lr = make_soft_mask(
        [[(182, 268), (222, 282), (188, 396), (65, 396), (65, 332), (148, 310)]],
        blur_radius=8,
    )
    # Protect head & compound eyes (105..215, 175..268)
    m_head_protect = make_soft_mask(
        [[(102, 172), (218, 172), (218, 268), (102, 268)]], blur_radius=7
    )
    m_pincer_ul = np.clip(m_pincer_ul * (1.0 - 0.9 * m_head_protect), 0.0, 1.0)
    m_pincer_lr = np.clip(m_pincer_lr * (1.0 - 0.9 * m_head_protect), 0.0, 1.0)

    # 3. Scorpion tail & stinger: pivot at tail base (315, 135)
    m_tail = make_soft_mask(
        [[(190, 4), (368, 4), (368, 148), (275, 120), (190, 98)]], blur_radius=9
    )
    m_stinger_sub = make_soft_mask(
        [[(195, 10), (305, 10), (285, 95), (195, 95)]], blur_radius=8
    )

    # 4. Five bottom-right walking legs
    leg_br_specs = [
        ([(222, 255), (255, 250), (272, 345), (218, 345)], 238, 262),
        ([(256, 235), (288, 228), (332, 305), (280, 315)], 268, 242),
        ([(282, 215), (312, 205), (365, 278), (328, 290)], 294, 220),
        ([(306, 192), (334, 182), (382, 248), (352, 260)], 318, 198),
        ([(328, 168), (358, 158), (398, 215), (370, 228)], 338, 176),
    ]
    m_legs_br = [
        (make_soft_mask([poly], blur_radius=6), rx, ry)
        for (poly, rx, ry) in leg_br_specs
    ]

    # 5. Four upper-left leg tips
    leg_ul_specs = [
        ([(68, 172), (112, 172), (105, 208), (62, 205)], 102, 195),
        ([(105, 145), (152, 145), (145, 178), (102, 175)], 142, 168),
        ([(148, 120), (196, 120), (188, 152), (145, 148)], 185, 142),
        ([(192, 98), (242, 98), (235, 130), (190, 125)], 230, 120),
    ]
    m_legs_ul = [
        (make_soft_mask([poly], blur_radius=6), rx, ry)
        for (poly, rx, ry) in leg_ul_specs
    ]

    # Normalize partition of unity so sum(masks) + m_body == 1.0 everywhere
    limb_list = (
        [m_pincer_ul, m_pincer_lr, m_tail]
        + [m for (m, _, _) in m_legs_br]
        + [m for (m, _, _) in m_legs_ul]
    )
    limb_sum = np.sum(limb_list, axis=0)
    scale_down = np.where(limb_sum > 1.0, 1.0 / np.maximum(limb_sum, 1e-5), 1.0)
    m_pincer_ul = m_pincer_ul * scale_down
    m_pincer_lr = m_pincer_lr * scale_down
    m_tail = m_tail * scale_down
    m_legs_br = [(m * scale_down, rx, ry) for (m, rx, ry) in m_legs_br]
    m_legs_ul = [(m * scale_down, rx, ry) for (m, rx, ry) in m_legs_ul]
    m_body = np.clip(1.0 - np.sum(
        [m_pincer_ul, m_pincer_lr, m_tail]
        + [m for (m, _, _) in m_legs_br]
        + [m for (m, _, _) in m_legs_ul],
        axis=0,
    ), 0.0, 1.0)

    mask_thorax = make_radial_mask(225, 185, 85, 65, blur_radius=12)
    y_grid, x_grid = np.mgrid[0:WORK_S, 0:WORK_S].astype(np.float32)

    def render_reaper_pose(
        body_dx_val,
        body_dy_val,
        breath_val,
        jaw_ul_ang,
        jaw_lr_ang,
        tail_ang,
        stinger_extra_ang,
        leg_br_angles,
        leg_ul_angles,
        squash_y=0.0,
    ):
        b_dx = np.full((WORK_S, WORK_S), body_dx_val, dtype=np.float32)
        b_dy = np.full((WORK_S, WORK_S), body_dy_val, dtype=np.float32)
        if breath_val != 0.0:
            b_dx += mask_thorax * ((x_grid - 225.0) / 85.0) * breath_val
            b_dy += mask_thorax * ((y_grid - 185.0) / 65.0) * breath_val
        if squash_y != 0.0:
            b_dy += ((y_grid - 200.0) / 200.0) * squash_y
            b_dx += ((x_grid - 200.0) / 200.0) * (-squash_y * 0.6)

        layers = [(m_body, b_dx, b_dy)]

        # Jaws rotate purely around their anatomical roots (105, 225) and (185, 275)
        ul_dx, ul_dy = rotation_field(105, 225, jaw_ul_ang, b_dx, b_dy)
        lr_dx, lr_dy = rotation_field(185, 275, jaw_lr_ang, b_dx, b_dy)
        layers.append((m_pincer_ul, ul_dx, ul_dy))
        layers.append((m_pincer_lr, lr_dx, lr_dy))

        # Tail rotates around (315, 135) + extra stinger curl around (265, 55)
        t_dx, t_dy = rotation_field(315, 135, tail_ang, b_dx, b_dy)
        if stinger_extra_ang != 0.0:
            s_dx, s_dy = rotation_field(265, 55, stinger_extra_ang, 0.0, 0.0)
            t_dx += m_stinger_sub * s_dx
            t_dy += m_stinger_sub * s_dy
        layers.append((m_tail, t_dx, t_dy))

        # 5 Bottom-Right Legs rotate purely around their roots (rx, ry)
        for (lmask, rx, ry), ang in zip(m_legs_br, leg_br_angles):
            ldx, ldy = rotation_field(rx, ry, ang, b_dx, b_dy)
            layers.append((lmask, ldx, ldy))

        # 4 Upper-Left Legs rotate purely around their roots (rx, ry)
        for (lmask, rx, ry), ang in zip(m_legs_ul, leg_ul_angles):
            ldx, ldy = rotation_field(rx, ry, ang, b_dx, b_dy)
            layers.append((lmask, ldx, ldy))

        return composite_skinned_layers(base, layers)

    # ---------------- WALK (8 FRAMES) ----------------
    walk_frames = []
    for f in range(8):
        phase = (f / 8.0) * 2.0 * math.pi
        body_sway_x = math.cos(phase) * 2.5
        body_bob_y = math.sin(phase * 2.0) * 3.5
        breath = math.sin(phase) * 2.5

        jaw_open = math.sin(phase) * 10.5
        tail_ang = math.sin(phase - 0.6) * 10.5
        stinger_ang = math.cos(phase - 0.6) * 8.0

        br_angs = [math.sin(phase + idx * 1.15) * 15.0 for idx in range(5)]
        ul_angs = [math.sin(phase + math.pi + idx * 1.2) * 13.0 for idx in range(4)]

        warped = render_reaper_pose(
            body_sway_x,
            body_bob_y,
            breath,
            jaw_open,
            -jaw_open,
            tail_ang,
            stinger_ang,
            br_angs,
            ul_angs,
        )
        draw = ImageDraw.Draw(warped)

        # Dripping neon-green venom droplets
        drip_prog = (f % 4) / 4.0
        for tip_x, tip_y in [(22, 315), (92, 368), (222, 82)]:
            drop_y = int(tip_y + drip_prog * 22)
            alpha_d = int(230 * (1.0 - drip_prog * 0.7))
            draw.rectangle(
                [tip_x - 2, drop_y - 4, tip_x + 2, drop_y + 4],
                fill=(120, 255, 40, alpha_d),
            )
            draw.rectangle(
                [tip_x - 1, drop_y - 2, tip_x + 1, drop_y + 2],
                fill=(220, 255, 160, alpha_d),
            )

        walk_frames.append(finalize_frame(warped))

    # ---------------- ATTACK (8 FRAMES) ----------------
    attack_frames = []
    for f in range(8):
        if f == 0:
            # Frame 0: Burrow dig crouch
            warped = render_reaper_pose(
                0.0, 12.0, -2.0, -10.0, 10.0, -12.0, -6.0,
                [12.0, 10.0, 8.0, 6.0, 4.0], [-10.0, -8.0, -6.0, -4.0], squash_y=9.0
            )
            fx_mode = "burrow_dig"
        elif f == 1:
            # Frame 1: Burrow erupt upward leap
            warped = render_reaper_pose(
                -6.0, -14.0, 3.0, 16.0, -16.0, 14.0, 10.0,
                [-16.0] * 5, [12.0] * 4, squash_y=-6.0
            )
            fx_mode = "burrow_erupt"
        elif f == 2:
            # Frame 2: Landing slam
            warped = render_reaper_pose(
                -2.0, 6.0, 0.0, -6.0, 6.0, -6.0, -4.0,
                [12.0] * 5, [-8.0] * 4, squash_y=5.0
            )
            fx_mode = "burrow_land"
        elif f == 3:
            # Frame 3: Slash windup (rears back, pincers open wide)
            warped = render_reaper_pose(
                10.0, -8.0, 3.0, 18.0, -18.0, -10.0, -6.0,
                [-10.0, 8.0, -10.0, 8.0, -10.0], [8.0, -8.0, 8.0, -8.0]
            )
            fx_mode = "slash_windup"
        elif f == 4:
            # Frame 4: X-Scissor Guillotine Strike!
            warped = render_reaper_pose(
                -12.0, 8.0, -2.0, -16.0, 16.0, 12.0, 8.0,
                [14.0, -10.0, 14.0, -10.0, 14.0], [-10.0, 10.0, -10.0, 10.0]
            )
            fx_mode = "slash_strike"
        elif f == 5:
            # Frame 5: Slash follow-through
            warped = render_reaper_pose(
                -6.0, 4.0, 0.0, -8.0, 8.0, 6.0, 4.0,
                [6.0, -6.0, 6.0, -6.0, 6.0], [-5.0, 5.0, -5.0, 5.0]
            )
            fx_mode = "slash_follow"
        elif f == 6:
            # Frame 6: Scorpion tail arches forward to charge acid spit
            warped = render_reaper_pose(
                2.0, -2.0, 2.0, 10.0, -10.0, -18.0, -14.0,
                [-6.0, 6.0, -6.0, 6.0, -6.0], [6.0, -6.0, 6.0, -6.0]
            )
            fx_mode = "tail_charge"
        else:
            # Frame 7: Venom barrage spit!
            warped = render_reaper_pose(
                -5.0, 3.0, -2.0, 14.0, -14.0, -24.0, -18.0,
                [10.0, -8.0, 10.0, -8.0, 10.0], [-8.0, 8.0, -8.0, 8.0]
            )
            fx_mode = "tail_spit"

        draw = ImageDraw.Draw(warped)
        if fx_mode == "burrow_dig":
            for cx, cy, r in [(65, 365, 8), (145, 380, 10), (245, 355, 9), (310, 320, 7), (45, 325, 6)]:
                draw.rectangle([cx - r, cy - r, cx + r, cy + r], fill=(58, 42, 28, 235), outline=(20, 14, 10, 255))
                draw.rectangle([cx - r // 2, cy - r // 2, cx + r // 2, cy + r // 2], fill=(110, 235, 45, 210))
        elif fx_mode == "burrow_erupt":
            for lx, ly in [(55, 350), (120, 375), (210, 365), (285, 330)]:
                draw.rectangle([lx - 3, ly - 28, lx + 3, ly + 8], fill=(135, 255, 65, 220))
                draw.rectangle([lx - 1, ly - 24, lx + 1, ly + 4], fill=(230, 255, 195, 240))
        elif fx_mode == "slash_windup":
            for sx, sy in [(25, 295), (55, 330), (95, 360)]:
                draw.rectangle([sx - 5, sy - 5, sx + 5, sy + 5], fill=(130, 255, 50, 220))
                draw.rectangle([sx - 2, sy - 2, sx + 2, sy + 2], fill=(240, 255, 210, 255))
        elif fx_mode == "slash_strike":
            slash_layer = Image.new("RGBA", (WORK_S, WORK_S), (0, 0, 0, 0))
            sd = ImageDraw.Draw(slash_layer)
            sd.arc([8, 210, 195, 392], start=115, end=265, fill=(40, 210, 30, 245), width=18)
            sd.arc([14, 216, 189, 386], start=122, end=258, fill=(155, 255, 70, 255), width=10)
            sd.arc([20, 222, 183, 380], start=130, end=250, fill=(240, 255, 215, 255), width=4)
            sd.line([(18, 245), (165, 382)], fill=(90, 250, 45, 240), width=12)
            sd.line([(22, 249), (160, 378)], fill=(230, 255, 190, 255), width=5)
            sd.line([(155, 235), (22, 378)], fill=(90, 250, 45, 240), width=12)
            sd.line([(150, 240), (26, 374)], fill=(230, 255, 190, 255), width=5)
            warped = Image.alpha_composite(warped, slash_layer)
        elif fx_mode == "slash_follow":
            slash_layer = Image.new("RGBA", (WORK_S, WORK_S), (0, 0, 0, 0))
            sd = ImageDraw.Draw(slash_layer)
            sd.arc([6, 215, 190, 392], start=125, end=255, fill=(80, 235, 40, 175), width=9)
            sd.arc([12, 221, 184, 386], start=132, end=248, fill=(210, 255, 160, 190), width=4)
            warped = Image.alpha_composite(warped, slash_layer)
        elif fx_mode == "tail_charge":
            orb = Image.new("RGBA", (WORK_S, WORK_S), (0, 0, 0, 0))
            od = ImageDraw.Draw(orb)
            scx, scy = 198, 86
            od.ellipse([scx - 22, scy - 22, scx + 22, scy + 22], fill=(80, 235, 30, 165))
            od.ellipse([scx - 14, scy - 14, scx + 14, scy + 14], fill=(165, 255, 75, 235))
            od.ellipse([scx - 7, scy - 7, scx + 7, scy + 7], fill=(245, 255, 220, 255))
            warped = Image.alpha_composite(warped, orb)
        elif fx_mode == "tail_spit":
            spit = Image.new("RGBA", (WORK_S, WORK_S), (0, 0, 0, 0))
            spd = ImageDraw.Draw(spit)
            scx, scy = 190, 92
            spd.ellipse([scx - 16, scy - 16, scx + 16, scy + 16], fill=(155, 255, 65, 230))
            for gx, gy, gr in [(142, 138, 12), (98, 182, 14), (54, 228, 11), (118, 215, 9)]:
                spd.line([(scx, scy), (gx, gy)], fill=(120, 245, 45, 195), width=5)
                spd.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(70, 215, 25, 240), outline=(20, 60, 10, 255))
                spd.ellipse([gx - gr // 2, gy - gr // 2, gx + gr // 2, gy + gr // 2], fill=(225, 255, 175, 255))
            warped = Image.alpha_composite(warped, spit)

        attack_frames.append(finalize_frame(warped))

    save_sheet(walk_frames, "img/monsters/boss_chitin_reaper_walk.webp")
    save_sheet(walk_frames, "img/monsters/boss_chitin_reaper_sheet.webp")
    save_sheet(attack_frames, "img/monsters/boss_chitin_reaper_attack.webp")
    return walk_frames, attack_frames


# ==============================================================================
# 2. PATIENT ZERO (Нулевой Пациент: Прародитель Кошмара) - DUAL-DOMAIN SKINNED MESH
# ==============================================================================
def build_patient_zero_sheets():
    base = load_work_img("img/monsters/boss_patient_zero.webp")

    # Exact Source-Domain Anatomical Masks in 400x400 space (verified on grid_pz.png):
    # 1. Screen-Left Chain-Wrapped Arm:
    #    Pivot at shoulder (76, 118). Strictly encloses the chain arm on the left.
    m_arm_left = make_soft_mask(
        [[(2, 96), (94, 108), (98, 195), (94, 275), (86, 314), (2, 314)]], blur_radius=6
    )

    # 2. Screen-Right Giant Bone-Claw Arm:
    #    Pivot at shoulder (248, 112). Strictly encloses the right arm & 4 bone claws.
    m_arm_right = make_soft_mask(
        [[(242, 78), (399, 78), (399, 385), (282, 385), (282, 364), (260, 356), (258, 220), (244, 160)]],
        blur_radius=6,
    )
    # Distal wrist/claws sub-weight for secondary claw whip around wrist (285, 200)
    m_claws_sub = make_soft_mask(
        [[(262, 185), (399, 185), (399, 385), (282, 385), (282, 364), (260, 356)]], blur_radius=8
    )

    # 3. Screen-Left Leg:
    #    Pivot at left hip (142, 238). Encloses left thigh, knee, shin, and foot.
    m_leg_left = make_soft_mask(
        [[(108, 236), (173, 236), (165, 310), (140, 396), (55, 396), (55, 338), (94, 316), (104, 275)]],
        blur_radius=6,
    )
    # Knee sub-weight for natural knee flexion around (115, 295)
    m_shin_left_sub = make_soft_mask(
        [[(55, 338), (94, 316), (104, 295), (165, 295), (140, 396), (55, 396)]], blur_radius=7
    )

    # 4. Screen-Right Leg:
    #    Pivot at right hip (206, 238). Encloses right thigh, knee, shin, and foot,
    #    strictly left of m_arm_right!
    m_leg_right = make_soft_mask(
        [[(176, 236), (242, 236), (254, 295), (256, 356), (278, 366), (278, 396), (190, 396), (185, 300)]],
        blur_radius=6,
    )
    m_shin_right_sub = make_soft_mask(
        [[(185, 295), (254, 295), (256, 356), (278, 366), (278, 396), (185, 396)]], blur_radius=7
    )

    # 5. Head: pivot at neck (202, 62)
    m_head = make_soft_mask(
        [[(168, 4), (238, 4), (238, 82), (168, 82)]], blur_radius=7
    )

    # Normalize Partition of Unity so sum(limbs) + m_torso == 1.0 everywhere on the source image
    limbs = [m_arm_left, m_arm_right, m_leg_left, m_leg_right, m_head]
    lsum = np.sum(limbs, axis=0)
    lscale = np.where(lsum > 1.0, 1.0 / np.maximum(lsum, 1e-5), 1.0)
    m_arm_left *= lscale
    m_arm_right *= lscale
    m_leg_left *= lscale
    m_leg_right *= lscale
    m_head *= lscale
    m_torso = np.clip(
        1.0 - (m_arm_left + m_arm_right + m_leg_left + m_leg_right + m_head),
        0.0,
        1.0,
    )

    # Internal torso feature masks (applied smoothly inside the torso/body field):
    # - Giant Yellow Shoulder Eyeball at (92, 68)
    mask_shoulder_eye = make_radial_mask(92, 68, 42, 40, blur_radius=7)
    mask_eye_pupil = make_radial_mask(92, 68, 22, 22, blur_radius=5)
    # - Vertical Rib-Maw Cavity at (182, 168)
    mask_rib_maw = make_radial_mask(182, 168, 48, 54, blur_radius=9)

    y_grid, x_grid = np.mgrid[0:WORK_S, 0:WORK_S].astype(np.float32)

    def render_pz_pose(
        body_dx_val,
        body_dy_val,
        arm_l_ang,
        arm_r_ang,
        claws_extra_ang,
        leg_l_ang,
        shin_l_ang,
        leg_r_ang,
        shin_r_ang,
        head_ang,
        maw_open_px=0.0,
        eye_bulge=0.0,
        pupil_dx=0.0,
        pupil_dy=0.0,
    ):
        # Base torso displacement field
        t_dx = np.full((WORK_S, WORK_S), body_dx_val, dtype=np.float32)
        t_dy = np.full((WORK_S, WORK_S), body_dy_val, dtype=np.float32)

        # Rib-maw horizontal parting around x=182 (zero at joints!)
        if maw_open_px != 0.0:
            # Smooth horizontal stretch sin((x - 182)/48 * pi/2)
            maw_profile = np.clip((x_grid - 182.0) / 28.0, -1.0, 1.0)
            t_dx += mask_rib_maw * maw_profile * maw_open_px

        # Shoulder eye bulge & pupil tracking at (92, 68)
        if eye_bulge != 0.0:
            t_dx += mask_shoulder_eye * ((x_grid - 92.0) * eye_bulge)
            t_dy += mask_shoulder_eye * ((y_grid - 68.0) * eye_bulge)
        if pupil_dx != 0.0 or pupil_dy != 0.0:
            t_dx += mask_eye_pupil * pupil_dx
            t_dy += mask_eye_pupil * pupil_dy

        layers = [(m_torso, t_dx, t_dy)]

        # 1. Left Chain Arm rotates purely around shoulder pivot (76, 118)
        al_dx, al_dy = rotation_field(76, 118, arm_l_ang, t_dx, t_dy)
        layers.append((m_arm_left, al_dx, al_dy))

        # 2. Right Giant Bone-Claw Arm rotates around shoulder (248, 112) + wrist (285, 200)
        ar_dx, ar_dy = rotation_field(248, 112, arm_r_ang, t_dx, t_dy)
        if claws_extra_ang != 0.0:
            cw_dx, cw_dy = rotation_field(285, 200, claws_extra_ang, 0.0, 0.0)
            ar_dx += m_claws_sub * cw_dx
            ar_dy += m_claws_sub * cw_dy
        layers.append((m_arm_right, ar_dx, ar_dy))

        # 3. Left Leg rotates around hip (142, 238) + knee (115, 295)
        ll_dx, ll_dy = rotation_field(142, 238, leg_l_ang, t_dx, t_dy)
        if shin_l_ang != 0.0:
            sl_dx, sl_dy = rotation_field(115, 295, shin_l_ang, 0.0, 0.0)
            ll_dx += m_shin_left_sub * sl_dx
            ll_dy += m_shin_left_sub * sl_dy
        layers.append((m_leg_left, ll_dx, ll_dy))

        # 4. Right Leg rotates around hip (206, 238) + knee (232, 295)
        lr_dx, lr_dy = rotation_field(206, 238, leg_r_ang, t_dx, t_dy)
        if shin_r_ang != 0.0:
            sr_dx, sr_dy = rotation_field(232, 295, shin_r_ang, 0.0, 0.0)
            lr_dx += m_shin_right_sub * sr_dx
            lr_dy += m_shin_right_sub * sr_dy
        layers.append((m_leg_right, lr_dx, lr_dy))

        # 5. Head rotates around neck (202, 62)
        hd_dx, hd_dy = rotation_field(202, 62, head_ang, t_dx, t_dy)
        layers.append((m_head, hd_dx, hd_dy))

        return composite_skinned_layers(base, layers)

    # ---------------- WALK (8 FRAMES) ----------------
    walk_frames = []
    for f in range(8):
        phase = (f / 8.0) * 2.0 * math.pi
        sway_x = math.sin(phase) * 3.5
        bob_y = abs(math.sin(phase)) * 5.5 - 2.5

        stride = math.sin(phase)
        l_lift = max(0.0, stride)
        r_lift = max(0.0, -stride)

        # Bipedal leg swing + natural knee bend on lifted leg
        leg_l_ang = stride * 12.0
        shin_l_ang = -l_lift * 10.0
        leg_r_ang = -stride * 12.0
        shin_r_ang = r_lift * 10.0

        # Counter-swinging arms
        arm_l_ang = -stride * 11.0
        arm_r_ang = stride * 10.0
        claws_ang = math.sin(phase - 0.6) * 8.0

        head_ang = math.sin(phase) * 4.5
        maw_open = (0.5 + 0.5 * math.sin(phase * 2.0)) * 4.0
        pup_x = math.cos(phase) * 4.5
        pup_y = math.sin(phase) * 3.5

        warped = render_pz_pose(
            sway_x,
            bob_y,
            arm_l_ang,
            arm_r_ang,
            claws_ang,
            leg_l_ang,
            shin_l_ang,
            leg_r_ang,
            shin_r_ang,
            head_ang,
            maw_open_px=maw_open,
            eye_bulge=0.04 * math.sin(phase * 2.0),
            pupil_dx=pup_x,
            pupil_dy=pup_y,
        )
        draw = ImageDraw.Draw(warped)

        # Heavy stomp dust puffs on contact frames (f == 2 and f == 6)
        if f in (2, 6):
            foot_x, foot_y = (92, 384) if f == 2 else (242, 384)
            for ox, oy, r in [(-18, 2, 7), (0, 5, 9), (18, 2, 7)]:
                draw.ellipse(
                    [foot_x + ox - r, foot_y + oy - r // 2, foot_x + ox + r, foot_y + oy + r // 2],
                    fill=(145, 45, 75, 175),
                )

        walk_frames.append(finalize_frame(warped))

    # ---------------- ATTACK (8 FRAMES) ----------------
    attack_frames = []
    for f in range(8):
        if f == 0:
            # Frame 0: Scythe windup — right bone-claw arm raises high (-22 deg), left chain arm cocks back (+16 deg)
            warped = render_pz_pose(
                2.0, -5.0, 16.0, -22.0, -10.0, -5.0, 0.0, 5.0, 0.0, -7.0,
                maw_open_px=3.0, eye_bulge=0.05, pupil_dx=-3.0, pupil_dy=-2.0
            )
            fx_mode = "scythe_windup"
        elif f == 1:
            # Frame 1: Scythe cleave impact! Right bone-claw arm slams inward-down (+18 deg), body lunges down
            warped = render_pz_pose(
                -5.0, 6.0, -16.0, 18.0, 12.0, 7.0, -5.0, -7.0, 5.0, 6.0,
                maw_open_px=5.0, eye_bulge=0.08, pupil_dx=-4.0, pupil_dy=4.0
            )
            fx_mode = "scythe_strike"
        elif f == 2:
            # Frame 2: Cleave follow-through & left chain-fist smash
            warped = render_pz_pose(
                -3.0, 4.0, -20.0, 10.0, 6.0, 4.0, 0.0, -4.0, 0.0, 3.0,
                maw_open_px=2.0
            )
            fx_mode = "scythe_follow"
        elif f == 3:
            # Frame 3: Ocular Laser Charge — shoulder eyeball at (92, 68) bulges outward
            warped = render_pz_pose(
                2.0, -2.0, 10.0, -8.0, -5.0, -3.0, 0.0, 3.0, 0.0, -4.0,
                maw_open_px=3.5, eye_bulge=0.22, pupil_dx=-2.0, pupil_dy=2.0
            )
            fx_mode = "laser_charge"
        elif f == 4:
            # Frame 4: Ocular Laser Fire!
            warped = render_pz_pose(
                4.0, -3.0, 14.0, -12.0, -6.0, -4.0, 0.0, 4.0, 0.0, -6.0,
                maw_open_px=5.0, eye_bulge=0.26, pupil_dx=-3.0, pupil_dy=3.0
            )
            fx_mode = "laser_fire"
        elif f == 5:
            # Frame 5: Laser dissipation
            warped = render_pz_pose(
                1.0, 0.0, 6.0, -5.0, 0.0, 0.0, 0.0, 0.0, 0.0, -2.0,
                maw_open_px=2.0, eye_bulge=0.10
            )
            fx_mode = "laser_after"
        elif f == 6:
            # Frame 6: Abyssal Rib-Maw Roar start — arms spread wide, rib-maw stretches open
            warped = render_pz_pose(
                0.0, -3.0, 16.0, -16.0, -8.0, -5.0, 0.0, 5.0, 0.0, -8.0,
                maw_open_px=6.5, eye_bulge=0.12
            )
            fx_mode = "roar_start"
        else:
            # Frame 7: Abyssal Rib-Maw Roar peak — maximum rib-maw parting + sonic shockwave rings
            warped = render_pz_pose(
                0.0, -5.0, 20.0, -20.0, -12.0, -7.0, 0.0, 7.0, 0.0, -11.0,
                maw_open_px=8.5, eye_bulge=0.18
            )
            fx_mode = "roar_peak"

        vfx = Image.new("RGBA", (WORK_S, WORK_S), (0, 0, 0, 0))
        vd = ImageDraw.Draw(vfx)

        if fx_mode == "scythe_windup":
            for cx, cy in [(310, 175), (348, 215), (375, 265), (335, 285)]:
                vd.rectangle([cx - 6, cy - 6, cx + 6, cy + 6], fill=(255, 40, 85, 215))
                vd.rectangle([cx - 3, cy - 3, cx + 3, cy + 3], fill=(255, 235, 140, 255))
        elif fx_mode == "scythe_strike":
            for offset, col, w_arc in [
                (0, (190, 15, 55, 245), 22),
                (6, (255, 55, 95, 255), 12),
                (12, (255, 235, 165, 255), 5),
            ]:
                vd.arc(
                    [65 + offset, 155 + offset, 392 - offset, 392 - offset],
                    start=345,
                    end=145,
                    fill=col,
                    width=w_arc,
                )
            for r_pad in [18, 36, 54]:
                vd.arc(
                    [65 + r_pad, 155 + r_pad, 392 - r_pad, 392 - r_pad],
                    start=355,
                    end=135,
                    fill=(255, 180, 120, 220),
                    width=4,
                )
        elif fx_mode == "scythe_follow":
            vd.arc([75, 175, 385, 390], start=5, end=140, fill=(220, 30, 70, 175), width=10)
            vd.ellipse([12, 295, 115, 345], outline=(255, 90, 120, 230), width=5)
            vd.ellipse([24, 305, 102, 335], outline=(255, 225, 160, 240), width=3)
        elif fx_mode == "laser_charge":
            ecx, ecy = 92, 68
            vd.ellipse([ecx - 48, ecy - 46, ecx + 48, ecy + 46], outline=(255, 45, 85, 220), width=5)
            vd.ellipse([ecx - 32, ecy - 30, ecx + 32, ecy + 30], outline=(255, 215, 70, 245), width=4)
            vd.ellipse([ecx - 14, ecy - 14, ecx + 14, ecy + 14], fill=(255, 250, 200, 245))
        elif fx_mode == "laser_fire":
            ecx, ecy = 92, 68
            tx, ty = 6, 365
            vd.line([(ecx, ecy), (tx, ty)], fill=(185, 15, 60, 220), width=36)
            vd.line([(ecx, ecy), (tx, ty)], fill=(255, 65, 105, 245), width=22)
            vd.line([(ecx, ecy), (tx, ty)], fill=(255, 215, 95, 255), width=12)
            vd.line([(ecx, ecy), (tx, ty)], fill=(255, 255, 240, 255), width=5)
            vd.ellipse([ecx - 34, ecy - 34, ecx + 34, ecy + 34], fill=(255, 70, 105, 230))
            vd.ellipse([ecx - 20, ecy - 20, ecx + 20, ecy + 20], fill=(255, 245, 185, 255))
        elif fx_mode == "laser_after":
            ecx, ecy = 92, 68
            vd.ellipse([ecx - 22, ecy - 22, ecx + 22, ecy + 22], outline=(255, 140, 90, 200), width=4)
            vd.line([(ecx, ecy), (20, 320)], fill=(255, 80, 110, 150), width=8)
        elif fx_mode == "roar_start":
            mcx, mcy = 182, 168
            vd.ellipse([mcx - 20, mcy - 48, mcx + 20, mcy + 48], fill=(255, 45, 85, 185))
            vd.ellipse([mcx - 10, mcy - 36, mcx + 10, mcy + 36], fill=(255, 230, 130, 235))
            vd.ellipse([mcx - 75, mcy - 75, mcx + 75, mcy + 75], outline=(255, 60, 105, 210), width=5)
        elif fx_mode == "roar_peak":
            mcx, mcy = 182, 168
            vd.ellipse([mcx - 24, mcy - 52, mcx + 24, mcy + 52], fill=(255, 60, 95, 210))
            vd.ellipse([mcx - 12, mcy - 40, mcx + 12, mcy + 40], fill=(255, 245, 175, 255))
            for rad, col, w_ring in [
                (95, (255, 220, 120, 240), 5),
                (145, (255, 50, 95, 225), 7),
                (188, (175, 20, 75, 185), 5),
            ]:
                vd.ellipse(
                    [mcx - rad, mcy - rad, mcx + rad, mcy + rad],
                    outline=col,
                    width=w_ring,
                )

        warped = Image.alpha_composite(warped, vfx)
        attack_frames.append(finalize_frame(warped))

    save_sheet(walk_frames, "img/monsters/boss_patient_zero_walk.webp")
    save_sheet(walk_frames, "img/monsters/boss_patient_zero_sheet.webp")
    save_sheet(attack_frames, "img/monsters/boss_patient_zero_attack.webp")
    return walk_frames, attack_frames


def save_sheet(frames, out_path):
    sheet = Image.new("RGBA", (CANVAS_W * len(frames), CANVAS_H), (0, 0, 0, 0))
    for i, fr in enumerate(frames):
        sheet.paste(fr, (i * CANVAS_W, 0))
    sheet.save(out_path, "WEBP", lossless=True, quality=100)
    print(f"Saved {out_path} ({sheet.size[0]}x{sheet.size[1]})")


def save_verification_contact_sheet(name, walk_frames, attack_frames, out_png):
    cols = 8
    rows = 2
    pad = 8
    w = cols * (CANVAS_W + pad) + pad
    h = rows * (CANVAS_H + pad) + pad
    canvas = Image.new("RGBA", (w, h), (26, 20, 28, 255))
    d = ImageDraw.Draw(canvas)

    for r_idx, frames in enumerate([walk_frames, attack_frames]):
        for c_idx, fr in enumerate(frames):
            x = pad + c_idx * (CANVAS_W + pad)
            y = pad + r_idx * (CANVAS_H + pad)
            d.rectangle([x, y, x + CANVAS_W - 1, y + CANVAS_H - 1], fill=(38, 30, 42, 255), outline=(80, 65, 90, 255))
            canvas.alpha_composite(fr, (x, y))

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
    r_walk, r_atk = build_chitin_reaper_sheets()
    save_verification_contact_sheet("reaper", r_walk, r_atk, "verify_reaper_sheets.png")

    p_walk, p_atk = build_patient_zero_sheets()
    save_verification_contact_sheet("pz", p_walk, p_atk, "verify_pz_sheets.png")

    artifact_dir = r"C:\Users\alexg\.gemini\antigravity\brain\5530d3d0-498e-42f4-b6db-b83d90eb69a6"
    save_gif(r_walk, rf"{artifact_dir}\boss_chitin_reaper_walk.gif", duration=95)
    save_gif(r_atk, rf"{artifact_dir}\boss_chitin_reaper_attack.gif", duration=115)
    save_gif(p_walk, rf"{artifact_dir}\boss_patient_zero_walk.gif", duration=105)
    save_gif(p_atk, rf"{artifact_dir}\boss_patient_zero_attack.gif", duration=115)
