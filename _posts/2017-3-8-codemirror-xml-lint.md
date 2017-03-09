---
layout: post
title: codemirror xml lint
tags: codemirror,editor,lint
datetime: 2017-3-8 11:56
---

{{ page.title }}
================
# About codemirror

CodeMirror is a code-editor component that can be embedded in Web pages. The core library provides only the editor component, no accompanying buttons, auto-completion, or other IDE functionality. It does provide a rich API on top of which such functionality can be straightforwardly implemented. See the addons included in the distribution, and the list of externally hosted addons, for reusable implementations of extra features.

CodeMirror works with language-specific modes. Modes are JavaScript programs that help color (and optionally indent) text written in a given language. The distribution comes with a number of modes (see the mode/ directory), and it isn't hard to write new ones for other languages.

<a href="https://github.com/codemirror/codemirror"><strong>github project</strong></a>

## codemirror lint addon

github仓库addon/lint/下可以找到lint插件.
像CSS,html,json之类是有统一标准的,都会有,而xml是需要schema的.

## codemirror css lint

<a href="http://codemirror.net/demo/lint.html">Codemirror linter demo page</a>

### 需要材料

#### CSSLint 用来负责实际的校验
<a href="https://github.com/CSSLint/csslint">CSSLint内核</a>

#### codmirror addon
lint处理框架:
> lint.js

#### csslint注册和触发器
> css-lint.js

#### codemirror配置

{% highlight javascript %}
CodeMirror({
    mode: "css",
    lint: true,
    lineNumbers: true,
    gutters: ['CodeMirror-lint-markers']
}) 
{% endhighlight %}

<p><img src="/assets/img/codemirror-css-lint.png"></p>

## xml lint

### xml schema

<a href="https://www.w3schools.com/xml/schema_intro.asp">xml schema</a>

{% highlight XML %}
<?xml version="1.0"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
<xs:element name="note">
  <xs:complexType>
    <xs:sequence>
      <xs:element name="to" type="xs:string"/>
      <xs:element name="from" type="xs:string"/>
      <xs:element name="heading" type="xs:string"/>
      <xs:element name="body" type="xs:string"/>
    </xs:sequence>
  </xs:complexType>
</xs:element>
</xs:schema>
{% endhighlight %}

### xml lint

<a href=https://github.com/kripken/xml.js">xml lint github</a>

### lint when codemirror change

{% highlight javascript %}
// require XML lint
var XMLLint = require('.xmllint.js');
// schema with root element name RootElement
var schema = ''
+ "<xsd:schema xmlns:xsd='http://www.w3.org/2001/XMLSchema'>"
+ "	<xsd:element name='RootElement'>"
+ "		<xsd:complexType>"
+ "			<xsd:sequence>"
+ "				<xsd:any minOccurs='0' maxOccurs='unbounded' processContents='skip'/>"
+ "			</xsd:sequence>"
+ "		</xsd:complexType>"
+ "	</xsd:element>"
+ "</xsd:schema>"; 
var makeErrorMarker = function(err) {
    var marker = document.createElement('div');
    marker.className = 'CodeMirror-lint-marker-error';
    marker.innerHTML = '&nbsp;';
    marker.title = err.message;
    return marker;
}
function updateHints() {
  editor.operation(function(){
    // clean pre lint
    editor.clearGutter("CodeMirror-lint-markers");
    var xml = editor.getValue();
    /*
        output format: ["error1_description:line_number: detail", "error2_description:line_number: detail", ...]
    */
    outputs = XMLLint.validateXML({
        xml: [xml],
        schema: [schema]
    })
    for (var i = 0; i < outputs.errors.length; ++i) {
      var error = outputs.errors[i].split[':'];
      var line_number = parseInt(error[1], 10);
      var message = error.slice(2).join('');
      editor.setGutterMarker(line_number, "CodeMirror-lint-markers", makeErrorMarker(message));
    }
  });
}
window.onload = function() {
  var sc = document.getElementById("xml");
  window.editor = CodeMirror(document.getElementById("code"), {
    lineNumbers: true,
    mode: "xml",
    value: """"
  });
  var waiting;
  editor.on("change", function() {
    clearTimeout(waiting);
    waiting = setTimeout(updateHints, 500);
  });
  setTimeout(updateHints, 100);
};
{% endhighlight %}
