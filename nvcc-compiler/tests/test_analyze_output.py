import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / 'scripts' / 'analyze_output.py'
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        'analyze_output', SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AnalyzeOutputTests(unittest.TestCase):
    def test_analyze_ptx_counts_register_ranges(self):
        module = load_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            ptx_file = Path(tmpdir) / 'kernel.ptx'
            ptx_file.write_text(
                """
.visible .entry foo()
{
    .reg .b32 %r<6>;
    .reg .pred %p<2>;
    mov.u32 %r1, %tid.x;
}
""".lstrip()
            )

            info = module.analyze_ptx(str(ptx_file))

        self.assertEqual(info['register_usage'], {'b32': 6, 'pred': 2})

    def test_analyze_sass_counts_predicated_instructions(self):
        module = load_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            sass_file = Path(tmpdir) / 'kernel.sass'
            sass_file.write_text(
                """
Function : foo
/*0010*/                   MOV R1, c[0x0][0x28] ;
/*0018*/               @P0 BRA 0x30;
/*0020*/                   RET.ABS.NODEC R20 0x0;
""".lstrip()
            )

            info = module.analyze_sass(str(sass_file))

        self.assertEqual(info['total_instructions'], 3)
        self.assertEqual(info['instruction_types'], {
                         'MOV': 1, 'BRA': 1, 'RET': 1})
        self.assertEqual(info['control_flow']['branches'], 1)
        self.assertEqual(info['control_flow']['returns'], 1)


if __name__ == '__main__':
    unittest.main()
