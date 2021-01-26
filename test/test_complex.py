import torch
import io
from torch.testing._internal.common_device_type import instantiate_device_type_tests, dtypes
from torch.testing._internal.common_utils import TestCase, run_tests
from torch.testing._internal.jit_utils import JitTestCase

devices = (torch.device('cpu'), torch.device('cuda:0'))

class TestComplex(JitTestCase):
    def test_script(self):
        def fn(a: complex):
            return a

        self.checkScript(fn, (3 + 5j,))

    def test_pickle(self):
        class ComplexModule(torch.nn.Module):
            def __init__(self):
                super(ComplexModule, self).__init__()
                self.a = 3 + 5j

            def forward(self, b: int):
                return b

        scripted = torch.jit.script(ComplexModule())
        buffer = io.BytesIO()
        torch.jit.save(scripted, buffer)
        buffer.seek(0)
        loaded = torch.jit.load(buffer)
        self.assertEqual(loaded.a, 3 + 5j)

class TestComplexTensor(TestCase):
    @dtypes(*torch.testing.get_all_complex_dtypes())
    def test_to_list(self, device, dtype):
        # test that the complex float tensor has expected values and
        # there's no garbage value in the resultant list
        self.assertEqual(torch.zeros((2, 2), device=device, dtype=dtype).tolist(), [[0j, 0j], [0j, 0j]])

    @dtypes(torch.float32, torch.float64)
    def test_dtype_inference(self, device, dtype):
        # issue: https://github.com/pytorch/pytorch/issues/36834
        default_dtype = torch.get_default_dtype()
        torch.set_default_dtype(dtype)
        x = torch.tensor([3., 3. + 5.j], device=device)
        torch.set_default_dtype(default_dtype)
        self.assertEqual(x.dtype, torch.cdouble if dtype == torch.float64 else torch.cfloat)

instantiate_device_type_tests(TestComplexTensor, globals())

if __name__ == '__main__':
    run_tests()
