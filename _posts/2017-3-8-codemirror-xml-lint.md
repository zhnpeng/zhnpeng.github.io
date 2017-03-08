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

<a href="http://codemirror.net/demo/lint.html">CM linter demo page</a>

### 需要材料

#### CSSLint
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

## xml lint

### xml schema

<a href="https://www.w3schools.com/xml/schema_intro.asp">xml schema</a>

{% highlight html %}
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
var fs =require('fs');
// require XML lint
var XMLLint = require('.xmllint.js');
// load schema file
var schema = fs.readFileSync('xml_schema.xsd');

function updateHints() {
  editor.operation(function(){
    for (var i = 0; i < widgets.length; ++i)
      editor.removeLineWidget(widgets[i]);
    widgets.length = 0;

    var xml = editor.getValue();
    outputs = XMLLint.validateXML({
        xml: [xml],
        schema: [schema]
    })
    for (var i = 0; i < outputs.errors.length; ++i) {
      var err = JSHINT.errors[i];
      if (!err) continue;
      var msg = document.createElement("div");
      var icon = msg.appendChild(document.createElement("span"));
      icon.innerHTML = "!!";
      icon.className = "lint-error-icon";
      msg.appendChild(document.createTextNode(err.reason));
      msg.className = "lint-error";
      widgets.push(editor.addLineWidget(err.line - 1, msg, {coverGutter: false, noHScroll: true}));
    }
  });
  var info = editor.getScrollInfo();
  var after = editor.charCoords({line: editor.getCursor().line + 1, ch: 0}, "local").top;
  if (info.top + info.clientHeight < after)
    editor.scrollTo(null, after - info.clientHeight + 3);
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
