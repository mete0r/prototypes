#include <Python.h>


static PyObject* foo_system(PyObject *self, PyObject *args) {
    const char *command;
    int sts;

    if (!PyArg_ParseTuple(args, "s", &command)) {
	return NULL;
    }

    sts = system(command);
    return Py_BuildValue("i", sts);
}


static PyMethodDef FooMethods[] = {
    {
	"system", foo_system, METH_VARARGS, "Execute a shell command."
    }, {
	NULL, NULL, 0, NULL,
    }
};

#if PY_MAJOR_VERSION >= 3
static char module_doc[] = "C optimization for foo\n\n";
static struct PyModuleDef _foo_module = {
    PyModuleDef_HEAD_INIT,
    "_foo",
    module_doc,
    -1,
    FooMethods,
    NULL,
    NULL,
    NULL,
    NULL
};
#endif


static PyObject* init(void) {
    PyObject *m;

#if PY_MAJOR_VERSION < 3
    m = Py_InitModule3("_foo", FooMethods, "C optimizations for foo\n\n");
#else
    m = PyModule_Create(&_foo_module);
#endif
    if (m == NULL) {
	return NULL;
    }
    return m;
}


PyMODINIT_FUNC
#if PY_MAJOR_VERSION < 3
init_foo(void) {
    init();
}
#else
PyInit__foo(void) {
    return init();
}
#endif
