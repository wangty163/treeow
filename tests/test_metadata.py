import json
import pathlib
import unittest


REPO_ROOT = pathlib.Path(__file__).parents[1]


class RepositoryMetadataTests(unittest.TestCase):
    def test_manifest_points_to_wangty163_maintenance_source(self):
        manifest_path = (
            REPO_ROOT / "custom_components" / "treeow" / "manifest.json"
        )
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        self.assertEqual(manifest["codeowners"], ["@wangty163"])
        self.assertEqual(
            manifest["documentation"],
            "https://github.com/wangty163/treeow",
        )
        self.assertEqual(
            manifest["issue_tracker"],
            "https://github.com/wangty163/treeow/issues",
        )
        self.assertEqual(manifest["version"], "1.0.6")

    def test_readme_has_no_old_repository_links(self):
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertNotIn("tuzkiyoung/treeow", readme)
        self.assertIn("wangty163/treeow", readme)


if __name__ == "__main__":
    unittest.main()
