// Copyright 2018 Google Inc. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package grumpy

import (
	"reflect"
	"sync"
)

var (
	callableIteratorType = newBasisType("callable-iterator", reflect.TypeOf(callableIterator{}), toCallableIteratorUnsafe, ObjectType)
)

type callableIterator struct {
	Object
	callable *Object
	sentinel *Object
	mutex    sync.Mutex
}

func newCallableIterator(callable *Object, sentinel *Object) *Object {
	iter := &callableIterator{Object: Object{typ: callableIteratorType}, callable: callable, sentinel: sentinel}
	return &iter.Object
}

func toCallableIteratorUnsafe(o *Object) *callableIterator {
	return (*callableIterator)(o.toPointer())
}

func callableIteratorIter(f *Frame, o *Object) (*Object, *BaseException) {
	return o, nil
}

func callableIteratorNext(f *Frame, o *Object) (item *Object, raised *BaseException) {
	i := toCallableIteratorUnsafe(o)
	i.mutex.Lock()
	defer i.mutex.Unlock()
	if i.callable == nil {
		raised = f.Raise(StopIterationType.ToObject(), nil, nil)
	} else if item, raised = i.callable.Call(f, Args{}, nil); raised == nil {
		var eq *Object
		if eq, raised = Eq(f, item, i.sentinel); raised == nil && eq == True.ToObject() {
			i.callable = nil
			item = nil
			raised = f.Raise(StopIterationType.ToObject(), nil, nil)
		}
	}
	return item, raised
}

func initCallableIteratorType(map[string]*Object) {
	callableIteratorType.flags &= ^(typeFlagBasetype | typeFlagInstantiable)
	callableIteratorType.slots.Iter = &unaryOpSlot{callableIteratorIter}
	callableIteratorType.slots.Next = &unaryOpSlot{callableIteratorNext}
}
