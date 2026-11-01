def main():
    with open('index.html', 'r', encoding='utf-8') as f:
        text = f.read()

    old_block = """const bossCyberCerberusImg=new Image();bossCyberCerberusImg.src='img/monsters/boss_cyber_cerberus.webp';
const bossCyberCerberusSheetImg=new Image();bossCyberCerberusSheetImg.src='img/monsters/boss_cyber_cerberus_sheet.webp';
const bossBioButcherImg=new Image();bossBioButcherImg.src='img/monsters/boss_bio_butcher.webp';
const bossBioButcherSheetImg=new Image();bossBioButcherSheetImg.src='img/monsters/boss_bio_butcher_sheet.webp';
const bossChitinReaperImg=new Image();bossChitinReaperImg.src='img/monsters/boss_chitin_reaper.webp';
const bossChitinReaperSheetImg=new Image();bossChitinReaperSheetImg.src='img/monsters/boss_chitin_reaper_sheet.webp';
const bossNeuroOvermindImg=new Image();bossNeuroOvermindImg.src='img/monsters/boss_neuro_overmind.webp';
const bossNeuroOvermindSheetImg=new Image();bossNeuroOvermindSheetImg.src='img/monsters/boss_neuro_overmind_sheet.webp';
const bossPatientZeroImg=new Image();bossPatientZeroImg.src='img/monsters/boss_patient_zero.webp';
const bossPatientZeroSheetImg=new Image();bossPatientZeroSheetImg.src='img/monsters/boss_patient_zero_sheet.webp';"""

    new_block = """const bossCyberCerberusImg=new Image();bossCyberCerberusImg.src='img/monsters/boss_cyber_cerberus.webp';
const bossCyberCerberusSheetImg=new Image();bossCyberCerberusSheetImg.src='img/monsters/boss_cyber_cerberus_sheet.webp';
const bossCyberCerberusWalkImg=new Image();bossCyberCerberusWalkImg.src='img/monsters/boss_cyber_cerberus_walk.webp';
const bossCyberCerberusAttackImg=new Image();bossCyberCerberusAttackImg.src='img/monsters/boss_cyber_cerberus_attack.webp';

const bossBioButcherImg=new Image();bossBioButcherImg.src='img/monsters/boss_bio_butcher.webp';
const bossBioButcherSheetImg=new Image();bossBioButcherSheetImg.src='img/monsters/boss_bio_butcher_sheet.webp';
const bossBioButcherWalkImg=new Image();bossBioButcherWalkImg.src='img/monsters/boss_bio_butcher_walk.webp';
const bossBioButcherAttackImg=new Image();bossBioButcherAttackImg.src='img/monsters/boss_bio_butcher_attack.webp';

const bossChitinReaperImg=new Image();bossChitinReaperImg.src='img/monsters/boss_chitin_reaper.webp';
const bossChitinReaperSheetImg=new Image();bossChitinReaperSheetImg.src='img/monsters/boss_chitin_reaper_sheet.webp';
const bossChitinReaperWalkImg=new Image();bossChitinReaperWalkImg.src='img/monsters/boss_chitin_reaper_walk.webp';
const bossChitinReaperAttackImg=new Image();bossChitinReaperAttackImg.src='img/monsters/boss_chitin_reaper_attack.webp';

const bossNeuroOvermindImg=new Image();bossNeuroOvermindImg.src='img/monsters/boss_neuro_overmind.webp';
const bossNeuroOvermindSheetImg=new Image();bossNeuroOvermindSheetImg.src='img/monsters/boss_neuro_overmind_sheet.webp';
const bossNeuroOvermindFloatImg=new Image();bossNeuroOvermindFloatImg.src='img/monsters/boss_neuro_overmind_float.webp';
const bossNeuroOvermindAttackImg=new Image();bossNeuroOvermindAttackImg.src='img/monsters/boss_neuro_overmind_attack.webp';

const bossPatientZeroImg=new Image();bossPatientZeroImg.src='img/monsters/boss_patient_zero.webp';
const bossPatientZeroSheetImg=new Image();bossPatientZeroSheetImg.src='img/monsters/boss_patient_zero_sheet.webp';
const bossPatientZeroWalkImg=new Image();bossPatientZeroWalkImg.src='img/monsters/boss_patient_zero_walk.webp';
const bossPatientZeroAttackImg=new Image();bossPatientZeroAttackImg.src='img/monsters/boss_patient_zero_attack.webp';"""

    if old_block in text:
        text = text.replace(old_block, new_block, 1)
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(text)
        print("Successfully declared all 10 boss animation sheet images!")
    else:
        print("ERROR: old_block not found in index.html!")

if __name__ == '__main__':
    main()
