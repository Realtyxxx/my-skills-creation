import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / 'scripts' / 'compile_ir.py'
)


def load_module():
    spec = importlib.util.spec_from_file_location('compile_ir', SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CompileIRTests(unittest.TestCase):
    def test_compile_cuda_respects_custom_output_path(self):
        module = load_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            source_file = tmpdir_path / 'kernel.cu'
            custom_output = tmpdir_path / 'custom-name.ptx'
            source_file.write_text('__global__ void kernel() {}\n')
            custom_output.write_text('// fake ptx\n')

            completed = SimpleNamespace(returncode=0, stdout='', stderr='')
            with mock.patch.object(
                module.subprocess,
                'run',
                return_value=completed,
            ):
                with contextlib.redirect_stdout(io.StringIO()):
                    result = module.compile_cuda(
                        str(source_file),
                        'ptx',
                        ['sm_80'],
                        [],
                        False,
                        False,
                        str(custom_output),
                    )

        self.assertEqual(result['output_files'], [str(custom_output)])

    def test_main_rejects_output_with_all(self):
        module = load_module()
        stderr = io.StringIO()

        with mock.patch.object(
            module.sys,
            'argv',
            [
                'compile_ir.py',
                '--input',
                'kernel.cu',
                '--output-type',
                'all',
                '--output',
                'combined.out',
            ],
        ):
            with contextlib.redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as exc:
                    module.main()

        self.assertEqual(exc.exception.code, 2)
        self.assertIn(
            '--output cannot be used with --output-type all', stderr.getvalue())


if __name__ == '__main__':
    unittest.main()
