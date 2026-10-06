# Local Contexts validator

`local-contexts.ttl` is a standalone SHACL extension for reviewing Local Contexts usage in catalogued records. It references the general IDN Catalogue Profile validator with `owl:imports`, but does not depend on a processor resolving that import when it is run on its own.

The validator targets `schema:CreativeWork`, `schema:Dataset`, and `schema:DataCatalog`, plus subjects that actually use `odrl:hasPolicy`, `schema:potentialAction`, or `dcat:qualifiedRelation`. This gives useful coverage for other catalogued resource types without requiring schema.org subclass entailment.

Its validation posture is advisory:

- `sh:Warning` identifies structural problems or departure from the preferred direct pattern.
- `sh:Info` reports use of the allowed qualified pattern so reviewers can confirm that relationship-level metadata is genuinely needed.
- There are currently no `sh:Violation` results.

Run it independently with:

```sh
kurra shacl validate --shacl resources/validators/local-contexts.ttl data.ttl
```

To apply both validators, supply or merge the general `resources/validator.ttl` shape graph as required by the SHACL processor being used. The `owl:imports` statement records the extension relationship but import resolution is processor-dependent.
