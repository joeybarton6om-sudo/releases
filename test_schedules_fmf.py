import struct
import unittest
from pathlib import Path

import schedules_fmf

DOSSIER = Path.home() / "Documents" / "Sports Interactive" / "Football Manager 27" / "schedules"


def _chaine(valeur: str) -> bytes:
    brut = valeur.encode("utf-8")
    return struct.pack("<I", len(brut)) + brut


def _annuaire() -> bytes:
    return (
        _chaine("Programme personnalisé")
        + struct.pack("<I", 2)
        + _chaine("image") + _chaine(".img") + struct.pack("<QQQ", 154, 63, 10) + bytes(16)
        + _chaine("Programme personnalisé") + _chaine(".tsc") + struct.pack("<QQQ", 217, 175, 150) + bytes(16)
    )


class TestSchedulesFmf(unittest.TestCase):
    def test_annuaire_decompose_le_nom_et_les_ressources(self):
        annuaire = schedules_fmf.lire_annuaire(_annuaire())
        self.assertEqual(annuaire["nom"], "Programme personnalisé")
        self.assertEqual(len(annuaire["ressources"]), 2)
        self.assertEqual(annuaire["ressources"][0]["extension"], ".img")
        self.assertEqual(annuaire["ressources"][0]["valeurs"], [154, 63, 10])
        self.assertEqual(annuaire["ressources"][1]["extension"], ".tsc")
        self.assertEqual(annuaire["ressources"][1]["valeurs"], [217, 175, 150])

    def test_comparateur_reperE_les_plages_divergentes(self):
        a = DOSSIER / "Programme personnalisé.fmf"
        if not a.is_file():
            self.skipTest("dossier des plannings indisponible")
        resultat = schedules_fmf.comparer(a, a)
        self.assertEqual(resultat["octets divergents"], 0)
        self.assertEqual(resultat["plages"], [])

    def test_lecture_du_dossier_utilisateur(self):
        if not DOSSIER.is_dir():
            self.skipTest("dossier des plannings indisponible")
        plannings = schedules_fmf.lire_dossier(DOSSIER)
        self.assertTrue(plannings)
        for planning in plannings:
            self.assertIn("fichier", planning)
            self.assertTrue(planning["fichier"].endswith(".fmf"))
            if planning.get("erreur") is None:
                self.assertTrue(planning["nom"])
                self.assertGreater(planning["annuaire"], 0)


if __name__ == "__main__":
    unittest.main()