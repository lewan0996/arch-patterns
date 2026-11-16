# Architecture record validator dependency review

Reviewed 2026-11-16 for local package `0.3.0`, issue #81. The validator uses
Python separately from the generated .NET runtime. Its installed resources
include exact requirements and require no catalog checkout or symlink.

| Package | Pin | License / ownership |
| --- | --- | --- |
| jsonschema | 4.23.0 | MIT; JSON Schema Draft 2020-12 validation |
| attrs | 25.4.0 | MIT; transitive immutable/value infrastructure |
| jsonschema-specifications | 2024.10.1 | MIT; bundled schema specifications |
| referencing | 0.36.2 | MIT; transitive schema-reference behavior |
| rpds-py | 0.29.0 | MIT; transitive persistent data structures; retain bundled notices |
| typing-extensions | 4.16.0 | PSF-2.0; compatibility types used by referencing on older Python |

Pins match the exercised installed graph (Python 3.14/Linux); CI also exercises
the Ubuntu Python toolchain. They are a reviewed increment, not a promise of
indefinite latest-version or platform compatibility. Use a disposable/local
virtual environment and retain distributed license/component notices. There is
no paid core dependency or managed-service subscription. No optional format
extras are installed. The validator only uses bundled/internal schema references;
record-provided schema URLs cannot trigger remote loading.

The Python standard library and tooling remain under their distribution terms.
No dependency is added to the generated .NET application/publish graph. Update
the exact requirements, compatibility review and checks together. Existing
framework/provider/image pins remain in [the service review](service-increment.md).

Primary sources: [versioned jsonschema validation documentation](https://python-jsonschema.readthedocs.io/en/v4.23.0/validate/),
[jsonschema metadata](https://pypi.org/project/jsonschema/4.23.0/),
[attrs](https://pypi.org/project/attrs/25.4.0/),
[schema specifications](https://pypi.org/project/jsonschema-specifications/2024.10.1/),
[referencing](https://pypi.org/project/referencing/0.36.2/),
[rpds-py](https://pypi.org/project/rpds-py/0.29.0/),
[typing extensions](https://pypi.org/project/typing-extensions/4.16.0/).
